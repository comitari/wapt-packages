def install():
    # Uninstalling other versions of the software (including switching from MSI to EXE)
    for to_uninstall in installed_softwares(name="^7-Zip"):
        if Version(to_uninstall["version"]) != Version(control.get_software_version()) or force:
            print("Removing: %s (%s)" % (to_uninstall["name"], to_uninstall["version"]))
            try:
                killalltasks(ensure_list(control.impacted_process))
                run(uninstall_cmd(to_uninstall["key"]))
                wait_uninstallkey_absent(to_uninstall["key"])
            except Exception as e:
                print(e)
                print("Remove failed: %s (%s)\nContinuing..." % (to_uninstall["name"], to_uninstall["version"]))

    # Installing the software
    bin_name = glob.glob("7z*.exe")[0]
    install_exe_if_needed(
        bin_name,
        "/S",
        "7-Zip",
        min_version=control.version.split("-", 1)[0],
    )

    # File association for 7-Zip
    for ext in ext_file_association:
        register_ext(
            "7-zip",
            ext,
            '"%s" "%%1"' % (makepath(app_dir, "7zFM.exe")),
            icon="%s,1" % (makepath(app_dir, "7z.dll")),
        )

    # Adding 7z in path
    add_to_system_path(app_dir)
