# euro-office-bin

EURO-OFFICE PER ARCH LINUX x86_64

Questo PKGBUILD riconfeziona il .deb amd64 ufficiale senza compilare il programma.
Release iniziale verificata: v9.3.5-2 (versione Arch 9.3.5.2-1).
Richiede circa 5 GB liberi durante la costruzione; installazione circa 1,5 GB.

INSTALLAZIONE

1. Conserva questa cartella in una posizione stabile.
2. Installa gli strumenti necessari (paru deve essere già disponibile):

   sudo pacman -Syu --needed base-devel python

3. Apri il terminale nella cartella contenente PKGBUILD e update.py:

   cd /home/enzo/Documents/ProgPKGBUILD/euro-office-bin
   python update.py --install

Esegui python, paru e makepkg come utente normale, senza sudo. Paru richiederà
autonomamente i privilegi per installare dipendenze e pacchetto.
Conferma l'installazione delle dipendenze proposte e del pacchetto risultante.
Il .deb viene scaricato dalla release fissata e verificato con SHA-256.
Non servono dpkg, apt o debtap.

AVVIO

Apri Euro-Office dal menu applicazioni, oppure esegui:

   euro-office

AGGIORNAMENTI FUTURI

Per cercare l'ultima release stabile, aggiornare il PKGBUILD e installarla:

   cd /home/enzo/Documents/ProgPKGBUILD/euro-office-bin
   python update.py --install

Se la versione è già installata, lo script non ricostruisce il pacchetto.
Al termine di un'installazione riuscita, o se il programma risulta già
aggiornato, elimina dalla cartella locale i .deb amd64 del programma,
i pacchetti euro-office-bin x86_64 .pkg.tar.zst/.xz/.gz e .SRCINFO.
Mantiene PKGBUILD, update.py, ISTRUZIONI.txt e gli altri file.
Se la costruzione o l'installazione fallisce, conserva i residui.
La pulizia riguarda solo questa cartella, non le cache globali di paru.
Per pulire i residui esistenti, senza contattare GitHub:

   python update.py --clean

La pulizia richiede che euro-office-bin risulti installato in pacman.
Usando direttamente paru -Bi . la pulizia automatica non viene eseguita:
in quel caso esegui python update.py --clean dopo l'installazione.
Per aggiornare soltanto il PKGBUILD ed esaminarlo prima della costruzione:

   python update.py
   less PKGBUILD
   paru -Bi .

Lo script seleziona la release indicata da GitHub come latest, esclude prerelease
e draft, seleziona soltanto il .deb amd64 del programma (non il pacchetto help),
e aggiorna versione, tag, nome del file e checksum ufficiale GitHub.
Non usa checksum SKIP o URL latest mobili durante la costruzione.
Una revisione upstream come 9.3.5-3 diventa 9.3.5.3: viene rilevata come upgrade.
Se cambiano formato versione, nome dell'asset, checksum della stessa versione o
struttura del pacchetto, si interrompe per richiedere un adattamento manuale.
Nuove release possono inoltre richiedere nuove dipendenze: questo non è
deducibile automaticamente dai soli metadati di GitHub.

IMPORTANTE: paru -Syu aggiorna repository e AUR, ma non controlla le release
GitHub di questo PKGBUILD privato. Per questo pacchetto usa il comando sopra.
Non è stato creato alcun aggiornamento pianificato. Per integrare un giorno gli
aggiornamenti in paru -Syu servirebbe mantenerlo su AUR o in un repository
pacman, aggiornando anche i metadati a ogni release.
In caso di limite API GitHub, riprova più tardi.

RIMOZIONE

   paru -Rns euro-office-bin

NOTE DI PACKAGING

Mantiene programma e librerie in /opt/euro-office/euro-office, launcher, icone
e voce nel menu ufficiali. Aggiunge il comando euro-office e rimuove l'alias
generico desktopeditors per evitare collisioni con ONLYOFFICE. Il launcher
usa Bash perché contiene una redirezione specifica di Bash. Gli script Debian
non vengono eseguiti; le cache desktop/icone sono gestite dagli hook Arch.
La guida offline opzionale pubblicata come pacchetto separato non è inclusa.

FONTI

Release: https://github.com/Euro-Office/DesktopEditors/releases
API: https://api.github.com/repos/Euro-Office/DesktopEditors/releases/latest
Paru (build locali): https://github.com/Morganamilo/paru#examples
