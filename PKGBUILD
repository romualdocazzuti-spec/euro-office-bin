# Repackages the official Debian amd64 binary; no Debian maintainer scripts run.
# Install with: python update.py --install
# update.py removes local build archives only after successful installation.
pkgname=euro-office-bin
pkgver=9.3.5.2
pkgrel=1
pkgdesc='Euro-Office desktop editors (official Debian amd64 binaries)'
arch=('x86_64')
url='https://github.com/Euro-Office/DesktopEditors'
license=('AGPL-3.0-only')
depends=(
  'alsa-lib' 'at-spi2-core' 'bash' 'brotli' 'bzip2' 'cairo' 'curl'
  'dbus' 'desktop-file-utils' 'expat' 'fontconfig' 'freetype2'
  'gcc-libs' 'glib2' 'glibc' 'gst-libav' 'gst-plugins-ugly' 'gtk3'
  'harfbuzz' 'hicolor-icon-theme' 'krb5' 'libcups' 'libdrm' 'libglvnd'
  'libnotify' 'libpulse' 'libx11' 'libxcb' 'libxcomposite' 'libxdamage'
  'libxext' 'libxfixes' 'libxkbcommon' 'libxkbcommon-x11' 'libxrandr'
  'libxss' 'mesa' 'nspr' 'nss' 'pango' 'ttf-carlito' 'ttf-dejavu'
  'ttf-liberation' 'wayland' 'xcb-util' 'xcb-util-cursor' 'xcb-util-image'
  'xcb-util-keysyms' 'xcb-util-renderutil' 'xcb-util-wm' 'xdg-user-dirs'
  'xdg-utils' 'zlib' 'zstd'
)
optdepends=('ttf-ms-fonts: Microsoft-compatible document fonts')
provides=("euro-office=${pkgver}")
conflicts=('euro-office' 'euro-office-euro-office')
options=('!strip' '!debug' '!lto')

# Updated by update.py. The upstream Debian revision is part of pkgver:
# v9.3.5-2 -> 9.3.5.2, so a future v9.3.5-3 is an upgrade too.
_tag='v9.3.5-2'
_deb='euro-office-euro-office_9.3.5-2_amd64.deb'
source=("${_deb}::${url}/releases/download/${_tag}/${_deb}")
noextract=("${_deb}")
sha256sums=('d1e9287bfb9278f69ca729e5df3d1dd260f58a2672f506a2efa64a4bb025e5a4')

package() {
  local -a payload
  local appdir="${pkgdir}/opt/euro-office/euro-office"
  mkdir -p "${srcdir}/deb-unpacked"
  bsdtar --no-same-owner -xf "${srcdir}/${_deb}" -C "${srcdir}/deb-unpacked"
  payload=("${srcdir}"/deb-unpacked/data.tar.*)
  if (( ${#payload[@]} != 1 )) || [[ ! -f ${payload[0]} ]]; then
    error 'Expected exactly one Debian data.tar payload'
    return 1
  fi
  bsdtar --no-same-owner -xf "${payload[0]}" -C "${pkgdir}"

  # Fail visibly if upstream changes its layout.
  [[ -x "${appdir}/DesktopEditors" ]] || return 1
  [[ -x "${pkgdir}/usr/bin/euro-office-euro-office" ]] || return 1
  [[ -f "${pkgdir}/usr/share/applications/euro-office-euro-office.desktop" ]] || return 1

  # Avoid the generic command shared with ONLYOFFICE. Keep upstream launcher.
  rm -f "${pkgdir}/usr/bin/desktopeditors"
  ln -s euro-office-euro-office "${pkgdir}/usr/bin/euro-office"
  # The upstream /bin/sh launcher uses Bash's &> redirection.
  sed -i '1s|^#!/bin/sh$|#!/bin/bash|' "${pkgdir}/usr/bin/euro-office-euro-office"

  # Arch provides desktop/icon cache refreshes through pacman hooks.
  # Debian control scripts are intentionally not installed or executed.
  if [[ -d "${pkgdir}/usr/share/licenses/euro-office-euro-office" ]]; then
    mv "${pkgdir}/usr/share/licenses/euro-office-euro-office" \
       "${pkgdir}/usr/share/licenses/${pkgname}"
  fi
}
