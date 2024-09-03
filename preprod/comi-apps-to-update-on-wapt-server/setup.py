# -*- coding: utf-8 -*-
from setuphelpers import *
import requests
import json
import smtplib
from configparser import ConfigParser
from waptpackage import HostCapabilities
from waptpackage import WaptRemoteRepo
from waptpackage import PackageVersion

all_package = {}

dict_host_capa = {
    "ubuntu22frx64": HostCapabilities(
        architecture="x64",
        language="fr",
        os="ubuntu",
        packages_locales=["fr", "en", "es", "de", "it"],
        tags=["debian", "debian_based", "linux", "unix", "debian11", "ubuntu-22"],
        os_version="11",
    ),
    "ubuntu20frx64": HostCapabilities(
        architecture="x64",
        language="fr",
        os="ubuntu",
        packages_locales=["fr", "en", "es", "de", "it"],
        tags=["debian", "debian_based", "linux", "unix", "debian11", "ubuntu-20"],
        os_version="11",
    ),
    "debian11frx64": HostCapabilities(
        architecture="x64",
        language="fr",
        os="debian",
        packages_locales=["fr", "en", "es", "de", "it"],
        tags=["debian-bullseye", "debian", "debian_based", "linux", "unix", "debian11", "debian-11"],
        os_version="11",
    ),
    "debian12frx64": HostCapabilities(
        architecture="x64",
        language="fr",
        os="debian",
        packages_locales=["fr", "en", "es", "de", "it"],
        tags=["debian-bookworm", "debian", "debian_based", "linux", "unix", "debian12", "debian-12"],
        os_version="11",
    ),
    "win10x64fr": HostCapabilities(
        architecture="x64",
        language="fr",
        os="windows",
        packages_locales=["fr", "en", "es", "de", "it"],
        tags=["windows-10", "win-10", "w-10", "windows10", "win10", "w10", "windows", "win", "w"],
        os_version="10.0.19043",
    ),
}

def install():
    plugin_inifiles = glob.glob("*.ini")

    for file in plugin_inifiles:
        if not isfile(makepath(WAPT.private_dir,file.split("\\")[-1])) :
            print(f"copie de {file} dans {WAPT.private_dir}")
            filecopyto(file, WAPT.private_dir)

def audit():
    plugin_inifile = makepath(WAPT.private_dir, "wapt_api.ini")
    conf_wapt = ConfigParser()
    conf_wapt.read(plugin_inifile)
    wapt_url = conf_wapt.get("wapt", "wapt_url")
    wapt_user = conf_wapt.get("wapt", "wapt_username")
    wapt_password = conf_wapt.get("wapt", "wapt_password")

    app_to_update_json_path = makepath(WAPT.private_dir, "app_to_update.json")
    if isfile(app_to_update_json_path):
        print("suppression de l'ancienne version du fichier json")
        remove_file(app_to_update_json_path)

    store = WaptRemoteRepo(name="main", url="https://wapt.tranquil.it/wapt", timeout=4, verify_cert=False)
    localstore = WaptRemoteRepo(name="main", url="https://srvwapt.comitari.fr/wapt", timeout=4, verify_cert=False)
    # Download JSON data from the URL
    online_package_list = {}
    local_package_list = {}
    for hc in dict_host_capa:
        online_package_version = {}
        for packageentry in store.packages():
            if dict_host_capa[hc].is_matching_package(packageentry):
                if not packageentry.package in online_package_version:
                    online_package_version[packageentry.package] = "0"
                if PackageVersion(online_package_version[packageentry.package]) < PackageVersion(packageentry.version):
                    online_package_version[packageentry.package] = packageentry.version
        online_package_list[hc] = online_package_version

    for hc in dict_host_capa:
        local_package_version = {}
        for packageentry in localstore.packages():
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