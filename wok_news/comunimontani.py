# -*- coding: utf-8 -*-
# import pdb
# import sys
import csv
# import string
# from datetime import date


class main:
    #
    # Run main if executed as a script
    if __name__ == "__main__":
        csv.register_dialect('zero', delimiter=',',
                             quotechar='\"',
                             quoting=csv.QUOTE_MINIMAL)
        csv_fn = "comunimontani.csv"
        txt_fn = "comunimontani.txt"
        txt_fd = open(txt_fn, "w")
        # pdb.set_trace()
        reg = ("",
               "Piemonte",
               "Valle d'Aosta",
               "Lombardia",
               "Trentino e Alto Adige/Südtirol",
               "Veneto",
               "Friuli e Venezia Giulia",
               "Liguria",
               "Emilia e Romagna",
               "Toscana",
               "Umbria",
               "Marche",
               "Lazio",
               "Abruzzo",
               "Molise",
               "Campania",
               "Puglia",
               "Basilicata",
               "Calabria",
               "Sicilia",
               "Sardegna")

        txt_fd.write("{{Template:Language_Toolbar}}\n\n")
        txt_fd.write("{| class=\"wikitable sortable\"\n")
        txt_fd.write("!Regione\n")
        for r in range(1, 21):
            txt_fd.write("|-\n")
            txt_fd.write(
                "|[[OpenERP/7.0/man/Comuni_Montani/{0}|{0}]]\n".
                format(reg[r].replace(' ', '_').replace('ü', 'u')))
        txt_fd.write("|}\n")
        txt_fd.close()

        for r in range(1, 21):
            fn = txt_fn.split('.')[0]
            txt_fd = open("{0}_{1:02d}.txt".format(fn, r), "w")
            if r > 1:
                prior = "/" + reg[r - 1].replace(' ', '_').replace('ü', 'u')
            else:
                prior = ""
            if r < 20:
                next = "/" + reg[r + 1].replace(' ', '_').replace('ü', 'u')
            else:
                next = ""
            sfx = "OpenERP/7.0/man/Comuni_Montani"
            txt_fd.write("{{{{Template:Language_Toolbar"
                         "|prior={0}{1}|next={0}{2}}}}}\n\n".
                         format(sfx, prior, next))
            csv_fd = open(csv_fn, "rb")
            csv_obj = csv.DictReader(
                csv_fd, fieldnames=[], restkey='undef_name', dialect='zero')
            hdr_read = False
            for row in csv_obj:
                if not hdr_read:
                    tb_dict = row['undef_name']
                    txt_fd.write("Regione {0}\n".format(reg[r]))
                    txt_fd.write("{| class=\"wikitable sortable\"\n")
                    txt_fd.write("!Codice Comune\n")
                    txt_fd.write("!Codice Catastale\n")
                    txt_fd.write("!Denominazione\n")
                    txt_fd.write("!Comune montano\n")
                    hdr_read = True
                    continue
                flds = row['undef_name']
                if int(flds[0]) == r:
                    if flds[7] == 'T':
                        flds[7] = "Totalmente"
                    elif flds[7] == 'P':
                        flds[7] = "Parzialmente"
                    elif flds[7] == 'NM':
                        flds[7] = "No"
                    txt_fd.write("|-\n")
                    i = 0
                    for f in tb_dict:
                        if i == 2:
                            txt_fd.write("|{0}{1}\n".format(
                                flds[1].strip().replace(' ', '0'),
                                flds[2].strip().replace(' ', '0')))
                        elif i == 3 or i == 4 or i == 7:
                            txt_fd.write("|{0}\n".format(flds[i].strip()))
                        i = i + 1
            txt_fd.write("|}\n")
            csv_fd.close()
            txt_fd.close()
