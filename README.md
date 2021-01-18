# STOPMOTION TOOL

# HOW TO USE 
1) Brancher l'ensemble des éléments au boitier.
* Camera USB (webcam, etc), sur un port USB 3 (bleu) [OBLIGATOIRE]
* Disque dur ou clé USB, sur un port USB 3 (bleu) [RECOMMANDé]
--> Si pas de disque externe branché, l'ensemble des images seront sauvegardées sur le Desktop du boitier
* Ecran [RECOMMANDé]
--> Il y a deux ports micro HDMI, possibilité d'utiliser des adaptateurs DVI
--> Sans écran le boitier fonctionnera quand même mais pas de preview / pelure d'oignon
* Clavier, souris [OPTIONNEL]

2) Brancher l'alimentation secteur sur le port USB-C
3) Démarrer le boitier en appuyant sur le bouton poussoir de l'alimentation secteur
4) Le boitier et son logiciel démarrent tout seuls
5) Lorsque la LED verte s'allume et que la vidéo s'affiche à l'écran, c'est bon !

# ATTENTION / NOTES
* Brancher la clé USD / DD et la caméra USB avant de démarrer le boitier (interrupteur)
* Le logiciel choisira le Disque Dur / Clé USB ayant le plus d'espace
* ! Attention ! Ne jamais retirer le Disque Dur / Clé USB avant d'avoir éteint le boitier, au risque de perdre des données / casser le disque dur

# Interface
Short press R : take
Short press G : preview anim
Long press R : new take
Long press G : quit (shutdonw RPi)

# LED :
    * la LED s'allume quand le programme de stopmotion est lancé
    * allumée : programme is running
    * clignote : pendant la capture d'image
    * s'éteint puis se rallume pendant la preview de l'animation

# Headless mode :
* Si la LED est allumée, c'est que le programme est lancé
Sinon... il y a un problème. --> vérifier le log file
* Le bouton vert (preview) ne sert qu'à éteindre (long press) le boitier, il n'y a pas de preview de l'animation

# keyboard shortcuts
c : show/hide console
t : take
p : preview anim
n : new take
f : toogle fulsscreen (buggy)
q : quit (return to command line / Desktop)
ESC : quit (will shutdon the RaspberryPi)
