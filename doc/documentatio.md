# Some notes


## Architektur

Die Bildverarbeitung, so ist diese teilweise in C++ geschrieben. Dasselbe gilt für Das Ansteuern der Kamera. Dazu wurde die NdkCamera API verwendet. 

* beschreiben mit ImageReader -> on_image * mit Diagramm etc. 

## Packages

Die Applikation Pilot kann grundsätzlich grob in packages aufgeteilt werden:

- log
Enthält diverse Tools, um 
- nanodet
- qrcode
- socket: Kommunikation mit dem Webserver über den Websocket Endpoint.
- bluetooth.terminal Kommunikation für Anhalten: Der Mikrokontroller wird "fremdgesteuert"
- shell: Erlaubt das Ausühren von UNIX-Befehlen als Root auf den Android Betriebssystem. 
- settings: Setzen von Parameter
