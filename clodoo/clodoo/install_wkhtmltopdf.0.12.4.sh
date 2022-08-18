#/bin/bash
ver="0.12.4"
echo "\$ cd /tmp"
cd /tmp
[ -f wkhtmltox-${ver}_linux-generic-amd64.tar.xz ] && rm -f wkhtmltox-${ver}_linux-generic-amd64.tar.xz
[ -d wkhtmltox ] && rm -fR wkhtmltox
echo "\$ wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/${ver}/wkhtmltox-${ver}_linux-generic-amd64.tar.xz"
wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/${ver}/wkhtmltox-${ver}_linux-generic-amd64.tar.xz
echo "\$ tar -xf wkhtmltox-${ver}_linux-generic-amd64.tar.xz"
tar -xvf wkhtmltox-${ver}_linux-generic-amd64.tar.xz
echo "\$ cd wkhtmltox"
cd wkhtmltox
for f in wkhtmltoimage wkhtmltopdf; do
    echo "\$ mv bin/$f /usr/local/bin/${f}.${ver}"
    mv bin/$f /usr/local/bin/${f}.${ver}
done
echo "\$ mv include/wkhtmltox /usr/local/include/wkhtmltox.${ver}"
mv include/wkhtmltox /usr/local/include/wkhtmltox.${ver}
for f in libwkhtmltox.so.${ver}; do
    echo "\$ mv lib/$f /usr/local/lib/$f"
    mv lib/$f /usr/local/lib/$f
done
for f in wkhtmltoimage wkhtmltopdf; do
    echo "\$ mv share/man/man1/${f}.1.gz /usr/local/share/man/man1/${f}.${ver}.1.gz"
    mv share/man/man1/${f}.1.gz /usr/local/share/man/man1/${f}.${ver}.1.gz
done
cd /tmp
rm -fR wkhtmltox
for f in wkhtmltoimage wkhtmltopdf; do
    echo "\$ ln -s /usr/local/bin/${f} /usr/bin/${f}.${ver}"
    ln -s /usr/local/bin/${f} /usr/bin/${f}.${ver}
done
