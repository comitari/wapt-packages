# -*- coding: utf-8 -*-
from setuphelpers import *
import requests
import json
import smtplib
import waptlicences
from configparser import ConfigParser
from waptpackage import HostCapabilities
from waptpackage import WaptRemoteRepo
from waptpackage import PackageVersion
from common import get_requests_client_cert_session

def install():
    plugin_inifiles = glob.glob("*.ini")

    for file in plugin_inifiles:
        if not isfile(makepath(WAPT.private_dir,file.split("\\")[-1])) :
            print(f"copie de {file} dans {WAPT.private_dir}")
            filecopyto(file, WAPT.private_dir)

def audit():

    CONFWAPT = ConfigParser()
    CONFWAPT.read(makepath(WAPT.private_dir, "wapt_api.ini"))
    username_wapt = CONFWAPT.get("wapt", "wapt_username")
    password_wapt = CONFWAPT.get("wapt", "wapt_password")

    dict_host_capa = {}

    t = waptlicences.waptserver_login(WAPT.config_filename,username_wapt,password_wapt)
    if not 'session' in t['session_cookies']:
        session_cookies = [u for u in t['session_cookies'] if u['Domain'] == WAPT.waptserver.server_url.split('://')[-1]][0]
    else:
        session_cookies = t['session_cookies']['session']
        session_cookies['Name'] = 'session'

    client_private_key_password = t["client_private_key_password"]

    sessionwapt = get_requests_client_cert_session(WAPT.waptserver.server_url,cert=(t['client_certificate'],t['client_private_key'],t['client_private_key_password']),verify=WAPT.waptserver.verify_cert)
    sessionwapt.cookies.set(session_cookies['Name'], session_cookies['Value'], domain=session_cookies['Domain'])
    sessionwapt.verify = WAPT.waptserver.verify_cert

    for pc in json.loads(sessionwapt.get("%s/api/v3/hosts?columns=host_capabilities&limit=1000000" % WAPT.waptserver.server_url).content)["result"]:
        if not pc['host_capabilities']:
            continue

        dict_capa = dict(architecture= pc['host_capabilities']['architecture'],
            language=pc['host_capabilities']['language'],
            os=pc['host_capabilities']['os'],
            packages_locales= sorted(pc['host_capabilities']['packages_locales']),
            tags=sorted(pc['host_capabilities']['tags']),
            os_version=pc['host_capabilities']['os_version'])

        tempo_capa = HostCapabilities(**dict_capa)

        dict_host_capa[str(dict_capa)] = tempo_capa

    store = WaptRemoteRepo(name="main", url='https://wapt.tranquil.it/wapt', timeout=4, verify_cert=True)
    localstore = WaptRemoteRepo(name="main", url= WAPT.waptserver.server_url + '/wapt', timeout=4, verify_cert=WAPT.waptserver.verify_cert)

    store_packages = store.packages()

    localstore.client_certificate = t['client_certificate']
    localstore.client_private_key = t['client_private_key']

    def give_password(location=None,identity=None):
        return client_private_key_password

    localstore.private_key_password_callback = give_password

    store_localstore = localstore.packages()

    # Download JSON data from the URL
    online_package_list = {}
    local_package_list = {}
    for hc in dict_host_capa:
        online_package_version = {}
        for packageentry in store_packages:
            if dict_host_capa[hc].is_matching_package(packageentry):
                if not packageentry.package in online_package_version:
                    online_package_version[packageentry.package] = "0"
                if PackageVersion(online_package_version[packageentry.package]) < PackageVersion(packageentry.version):
                    online_package_version[packageentry.package] = packageentry.version
        online_package_list[hc] = online_package_version

    for hc in dict_host_capa:
        local_package_version = {}
        for packageentry in store_localstore:
            if dict_host_capa[hc].is_matching_package(packageentry):
                if not packageentry.package in local_package_version:
                    local_package_version[packageentry.package] = "0"
                if PackageVersion(local_package_version[packageentry.package]) < PackageVersion(packageentry.version):
                    local_package_version[packageentry.package] = packageentry.version
        local_package_list[hc] = local_package_version

    list_app_to_update = []
    for hc in dict_host_capa:
        for app in local_package_list[hc]:
            if "-" in app:
                if "tis-" + app.split("-", 1)[1] in online_package_list[hc]:
                    if PackageVersion(local_package_list[hc][app]) < PackageVersion(online_package_list[hc]["tis-" + app.split("-", 1)[1]]) and app not in list_app_to_update:
                        print(
                            f'{app} new version detected from {local_package_list[hc][app]} to {online_package_list[hc]["tis-"+app.split("-", 1)[1]]} for {hc}'
                        )
                        list_app_to_update.append(
                            {
                                "package": app,
                                "old_version": local_package_list[hc][app],
                                "new_version": online_package_list[hc]["tis-" + app.split("-", 1)[1]],
                            }
                        )
    WAPT.write_audit_data_if_changed("apps_to_upgrade", "list", list_app_to_update, max_count=3)


    if not list_app_to_update:
        message="your repository seems up to date"
        print(message)
        #send_to_rocket(message)
        return "OK"
    else:
        message=f"You need to update some packages :\n"
        for app in list_app_to_update:
            message += f"**{app['package']}** : {app['new_version']} from  : {app['old_version']}\n"
        print(message)
        #send_to_rocket(message)
        send_email("Some application need to be updated on your wapt server",message)
        return "WARNING"


def send_to_rocket(message_text, attachments=None):
    """
    Envoie un message à Rocket.Chat via un webhook.
    
    :param message_text: Texte du message à envoyer
    :param attachments: Liste de pièces jointes (facultatif)
    """
    smtp_inifile = makepath(WAPT.private_dir, "rocket.ini")
    conf_wapt = ConfigParser()
    conf_wapt.read(smtp_inifile)

    webhook_url = conf_wapt.get("rocket", "url")
    
    # Construire le message

    message = {
        'text': message_text
    }
    if attachments:
        message['attachments'] = attachments

    # Envoyer la requête POST
    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
    
    # Vérifier la réponse
    if response.status_code == 200:
        print('Message envoyé avec succès.')
    else:
        print(f'Échec de l\'envoi du message. Statut de la réponse : {response.status_code}')
        print(f'Erreur : {response.text}')


def send_mail(body,subject):

    smtp_inifile = makepath(WAPT.private_dir, "smtp.ini")
    conf_wapt = ConfigParser()
    conf_wapt.read(smtp_inifile)

    from_addr = conf_wapt.get("smtp", "from_addr")
    to_addr = conf_wapt.get("smtp", "to_addr")
    password = conf_wapt.get("smtp", "password")
    smtpserver = conf_wapt.get("smtp", "smtpserver")

    print(from_addr)


    message = f"Subject: {subject}\n\n{body}"
    server = smtplib.SMTP(smtpserver, 587)
    server.starttls()
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, message)
    server.quit()
    return "OK"
