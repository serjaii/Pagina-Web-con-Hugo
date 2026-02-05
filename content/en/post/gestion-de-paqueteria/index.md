---
title: "Package Management Exercises"
date: 2025-11-22T14:00:00+01:00
description: "Practical exercises on package management in Debian: apt, dpkg, repositories, and .deb files"
image: cover.png
categories:
  - Systems
tags:
  - Debian
  - Apt
  - Dpkg
  - Repositories
---

# Package Management Exercises

**By:** Sergio Jimenez Suarez
**Course:** 2nd ASIR - IES Gonzalo Nazareno

---

## Working with apt, aptitude, dpkg

Prepare a virtual machine with Debian trixie, perform the following actions:

### 1. What actions do I achieve by performing apt update and apt upgrade. Explain in detail.

The command `apt update` constitutes the essential first step when upgrading packages. This procedure performs the following functions:

*   **Obtaining External Metadata:** `apt update` communicates with online software repositories to obtain metadata for available packages. This information includes details about the latest versions, their dependencies, and other important data.
*   **Refreshing Local Metadata Copy:** Subsequently, `apt` updates its local copy with this metadata. This allows the system to have immediate access to information about packages without needing to download it again.

```bash
sudo apt update
```

After updating the information about available packages, the next step is to execute the `apt upgrade` command. This command covers a series of key actions:

*   **Choice of Available Versions:** `apt` selects the versions that will be considered for the available packages. Normally, these are the most recent versions, although some exceptions can be made.
*   **Dependency Resolution:** `apt` is responsible for verifying and handling dependencies between packages to ensure that the update is performed consistently and that all dependencies are met.
*   **Package Download:** If new versions of packages are detected, `apt` proceeds to download them from online repositories to the local system cache.
*   **Package Extraction:** `apt` performs the extraction of the downloaded binary packages.
*   **Execution of Pre-installation Scripts:** During the update process, pre-installation scripts are carried out, which may include configurations and adjustments needed before the installation process.
*   **Binary Package Installation:** Next, the binary files of the new versions of the packages are installed on the system.
*   **Execution of Post-installation Scripts:** Finally, post-installation scripts are executed, which can carry out additional configurations after the installation is complete.

```bash
sudo apt upgrade
```

### 2. List the relation of packages that can be updated. What information can you get from what is shown in the listing?

As we already upgraded, it doesn't find packages for us, but the syntax would be as follows:

```bash
apt list --upgradable
```

**Format:** Package Name/Current Version - Available Version - Status - Package Description

### 3. Indicate the installed version, candidate, as well as the priority of the openssh-client package.

```bash
apt policy openssh-client
```

### 4. How can you get information about an official package installed or not installed?

```bash
apt show openssh-client
```

### 5. Get all the information you can from the openssh-client package currently installed on your machine.

```bash
dpkg -s openssh-client
```

### 6. Get all the information you can from the openssh-client package candidate for update on your machine.

```bash
apt show openssh-client
```

As we see there are no new candidates.

### 7. List all content referring to the current openssh-client package on your machine. Use both dpkg and apt.

With `dpkg`:

```bash
dpkg -L openssh-client
```

With `apt-file` (if installed):

```bash
apt-file list openssh-client
```

### 8. List the content of a package without the need to install or download it.

```bash
apt-file list openssh-client
```

### 9. Simulate the installation of the openssh-client package.

```bash
sudo apt install -s openssh-client
```

I already have openssh-client, I try another package since the operation is the same.

### 10. What command informs you of possible bugs present in a certain package?

```bash
apt-listbugs list openssh-client
```

### 11. After performing an apt update && apt upgrade. If you wanted to update only the packages containing the string openssh. What procedure would you follow?

Perform this action, with the repetitive structures offered by bash, as well as with the xargs command.

```bash
apt list --installed | grep openssh | cut -d/ -f1 | xargs sudo apt install --only-upgrade -y
```

### 12. How would you find which packages depend on a specific package?

```bash
apt-cache rdepends openssh-client
```

### 13. How would you proceed to find the package to which a certain file belongs?

```bash
dpkg -S /usr/bin/ssh
```

### 14. What procedures would you use to clear the cache regarding package downloads?

```bash
sudo apt clean
```

### 15. Perform the installation of the keyboard-configuration package passing the configuration parameter values as environment variables beforehand.

```bash
echo "keyboard-configuration keyboard-configuration/layoutcode string es" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive apt install keyboard-configuration
```

### 16. Reconfigure the locales package on your computer, adding a location that did not exist previously.

Check modifying the corresponding environment variables so that the user session uses another locale.

```bash
sudo dpkg-reconfigure locales
```

Check:

```bash
locale
```

### 17. Interrupt the configuration of a package and explain the steps to take to continue the installation.

We interrupt with `Ctl+C`, to resume it simply:

```bash
sudo dpkg --configure -a
```

### 18. Explain the instruction you would use to make a full update of all packages on your system in a completely non-interactive way.

```bash
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y
```

### 19. Lock the update of certain packages.

```bash
sudo apt-mark hold apache2
sudo apt-mark showhold
```

---

## Working with .deb files

### 1. Download a package without installing it, that is, download the corresponding .deb file. Indicate different ways to do it.

Copying the link from debian repositories and using wget:

```bash
wget http://ftp.es.debian.org/debian/pool/main/a/apache2/apache2_2.4.65-2_amd64.deb
```

With apt:

```bash
sudo apt download apache2
```

### 2. How can you view the content, not extract it, of what will be installed on the system from a deb package?

```bash
dpkg -c apache2_2.4.65-2_amd64.deb
```

### 3. On the downloaded .deb file, use the ar command.

`ar` allows extracting the content of a deb package. Indicate the procedure to visualize with ar the content of the deb package. With the package you downloaded and using the ar command, unzip the package. What information do you have after extraction? Indicate the purpose of what was extracted.

Visualize content:

```bash
ar t apache2_2.4.65-2_amd64.deb
```

Extract content:

```bash
ar x apache2_2.4.65-2_amd64.deb
```

Extracted content:
*   `debian-binary`: Deb format version.
*   `control.tar.xz`: Package metadata (dependencies, scripts, etc).
*   `data.tar.xz`: Program files.

### 4. Indicate the procedure to unzip what was extracted by ar in the previous point. What information does it contain?

```bash
tar -tf data.tar.xz
```

---

## Working with repositories

### 1. Add the trixie-backports and sid repositories to your sources.list file.

```bash
cat /etc/apt/sources.list
```

### 2. Configure the APT system so that debian trixie packages have higher priority and therefore are the ones installed by default.

File `/etc/apt/preferences.d/trixie`:

```text
Package: *
Pin: release n=trixie
Pin-Priority: 900
```

### 3. Configure the APT system so that trixie-backports packages have higher priority than those from unstable.

File `/etc/apt/preferences.d/trixie`:

```text
Package: *
Pin: release n=trixie
Pin-Priority: 900

Package: *
Pin: release n=trixie-backports
Pin-Priority: 750

Package: *
Pin: release n=unstable
Pin-Priority: 500
```

### 4. How do you add the possibility of downloading i386 architecture packages on your system?

What command have you used? List non-native architectures. How would you proceed to discard the possibility of downloading i386 architecture packages?

Add architecture:

```bash
sudo dpkg --add-architecture i386
sudo apt update
```

Remove architecture:

```bash
sudo dpkg --remove-architecture i386
sudo apt update
```

### 5. If you wanted to download a package, how can you know all the available versions of said package?

```bash
apt policy apache2
```

### 6. Indicate the procedure to download a package from the stable repository.

```bash
sudo apt download --target-release stable apache2
```

### 7. Indicate the procedure to download a package from the trixie-backports repository.

```bash
sudo apt download --target-release trixie-backports apache2
```

### 8. Indicate the procedure to download a package from the sid repository.

```bash
sudo apt download --target-release sid apache2
```

### 9. Indicate the procedure to download an i386 architecture package.

```bash
sudo apt download apache2:i386
```

---

## Working with directories

### 1. What are the purposes of:

**`/var/lib/apt/lists/`**
This directory saves the lists of packages offered by the repositories configured on your system. The files, with .list extension, include data such as package name, version, and repository address. When executing `apt update`, these lists are renewed with the latest information.

**`/var/lib/dpkg/available`**
This file collects information on packages available and installed on your system along with their versions. `dpkg` uses it to take inventory of what you have installed and to consult details about dependencies.

**`/var/lib/dpkg/status`**
It also contains information about installed packages, but more completely than available. It indicates the current status of each package: installed, removed, pending configuration, or with errors, thus offering more precise control to the package manager.

**`/var/cache/apt/archives/`**
Here, downloaded .deb files are stored before being installed. When you do an `apt-get install` or `apt-get upgrade`, packages are first downloaded to this directory and then installed. Keeping them is useful if you need to reinstall a package without having to download it again, saving time and connection.
