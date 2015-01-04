# Maintainer: Marshall Ward <marshall.ward@gmail.com>
pkgname=python-f90nml-git
pkgver=0.10.2
pkgrel=1
pkgdesc="A Fortran namelist parser for Python"
arch=('any')
url="https://github.com/marshallward/f90nml"
license=('Apache')
groups=()
depends=('python')
makedepends=('git')
optdepends=()
checkdepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=(!emptydirs)
install=
source=("python-f90nml-git::git+https://github.com/marshallward/f90nml#tag=v$pkgver")
noextract=()
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname"
    python setup.py install --root="$pkgdir/" --optimize=1
}
