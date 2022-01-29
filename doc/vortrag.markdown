
## Gesamtsystem Informatik

Analog zum Gesamtgerüst in der Mechanik, ist Informatiksystem auf vier Säulen aufgebaut.

Die erste Säule ist Objekterkennug, welche essentiell ist. 
Wir haben zwei verfügare Optionen, dazu kommen wir gleich.
Diese ganze Vorgang der Fahrt wird auf der Website dokumentiert. Wir schicken Logging Informationen sowohl als auch Bilder auf den Webserver. (dazu sehen wir später noch eine kleine Demo)
Die letzte Säule ist die Kommunikation mit dem Mikrokontroller. Wir Kommunizieren über Bluetooth. Das war eine bewusste Entscheidung, es gibt uns sehr viel Spielraum.

## Objekterkennung

Es steht fest: Das Fahrzeug muss anhalten. Warum muss es anhalten? Weil wir eine stabiles, qualitatives Bild machen wollen. Das natürlich _erheblich_ einfacher, wenn das Fahrzeug stillsteht.
Also stellt sich eine ganz grundsätzliche Frage: Wie halten wir an? Anhalten aufgrund von QR-Code oder Pflanze?
Beides ist technisch möglich.
Sie werden am Schluss dieser Präsentation sehen, welche der beiden Optionen in userem Kontext passt. Wir werden jetzt diese beiden Optionen etwas genauer betrachten.

## Video Folie 
### video starten
Ich habe ein System implementiert, um die Pflanzen zu erkennen. 
Die typische Frage, die hier meisten aufkommt: "Ja, aber die Fahrt ist ja einer Wiese. Erkennt es dann nicht andere Pflanzen, die nicht von interesse sind.?" 
Das denkt man im ersten Moment, ist aber kein Problem.

Die tatsächliche Art der Pflanze ist in diesem ersten Schritt noch nicht relevant.

## Diagramm 1
Wir verwenden ein Objekterkennungsmodel, welches unter anderem auf diese Klassen ausgerichtet ist. 


Das App teilt dem Mikrocontroller mit: "Hey! Ich habe eine Pflanze entdeckt. Wir müssen kurz anhalten. Die Mitteilung erfolgt innerhalb weniger Millisekdungen. Die Bluetooth Verbindung ist während der ganzen Fahrt aktiv. Nach dem Anhalten Signal kann das Fahrzeug natürlich nicht direkt weiter machen, man muss daran denken, dass es einen Bremsweg gibt.
Nachdem Angehalten wurde, geht es weiter.
Der QR Code wird gelesen. Beide diese Informationenen werden auf den Webserver geschickt. Das ist der grobe Ablauf. Jetzt schauen wir uns noch die zweite Methode an.


## Diagramm 2

Diese Idee nimmt ausschliesslich den QR- Code zum Anhalten.

Diese Methode ist stabiler. Und sie reduziert die Komplexität. Folglich werden wir uns wahrscheinlich diese Methode einsetzen am Wettbewerb. Es ist aber nicht so, dass wir die andere Art, also Erkennung der Topfpflanze (wie im Video gezeigt) nicht komplett vergessen. Wir werden diese Idee im Hinterkopf behalten. Und natürlich ist es praktisch, einen Plan B zu haben. Sollte sich herausstellen, dass die Erkennung des QR Codes als Object nicht funktionert, sind wir beruhigt, weil wir wissen, es gibt einen Plan B. 



## Entscheid Option 2

Option 2 ist unser Favorit. 
### keep it simpel
Ein sehr bekanntes Software design Prinzip ist KEEP IT SIMPLE. Das ist eigentlich fast eine Binsensweisheit. Der Programmieren hat gut daran, wenn er jeden Aspekt des Sytems so simpel wie möglich haltet.


# FPS
Tests haben ergeben, dass die Lösung, die nur den QR Code erkennt, deutlich effizienter ist. Effizienz ist definiert als die Arbeit pro Zeiteinheit. Und mit der QR-Code Lösung können mehr Bilder verarbeitet werden. 
# Schneller fahren
Als direkte Folge der vorherigen Aussage: Wir können schneller fahren, weil die Verarbeitungsgeschwindigkeit der Bilderkennung höhöer ist. Das freut uns natürlich. Wir wollen so schnell wie möglich sein. 



## Webserver: Video Demo


Hier: Demo Logs und Demo Bilder. Nach der Demo des Logging: Was ist jetzt hier passiert? 
1.) Das App hat eine Verbindung auf den Webserver aufgebaut. 
2.) Der Webserver akzeptiert die Verbindung. 
3.) Jetzt ist die Vebindung offen. Das heisst, wir haben einen Kommunikationskanal, in welchem wir in beide Richtungen Daten senden können. 
4.) Das App schickt periodisch Text-basierte Nachrichten und Bilder. Der Webserver akzeptiert diese und sendet sie an alle Clients weiter. Das hat den Effekt, dass neue Nachrichten erscheinen, ohne dass die Seite neu geladen werden muss.   



# Zusammenfassung
 
Einiges ist schon fertig gestellt. So funktioniert zum Beispiel die Pfaderkennung schon gut und das Fahrzeug korrigiert seine Fahrtrichtung, wenn es eine Kurve gibt. 

Für die Zukunft planen wir vor allem, viele Tests zu machen. Je komplexer ein System ist, desto höher ist die Wahrscheinlichkeit dass plötzlich ein Modul nicht so funktioniert, wie es gedacht war. Man sieht erst ob ein wirklich funktioniert, wenn man alle Teilelemente zusammensetzt.
Jetzt sind wir offen für fragen.