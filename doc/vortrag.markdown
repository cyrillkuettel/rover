# Präentation

## App

Zuerst ganz grundsätzliche Frage: Anhalten aufgrund von QR-Code oder Pflanze?
Beides ist technisch möglich.
- Idee 1:
	Anhalten basierend auf der Topfplanze

Das coco-dataset ist ein grosses Datenset, welches unter anderem auch Objekterkennung unterstützt. uNd hat eine ganze Reihe von Klassen. Für die Objekterkennung gibt es 80 mögliche Klassen. Praktischerweise ist eines davon "potted plant" und "vase". Das kommt sehr gelegen für uns. 


- Idee 2:
	Anhalten mit QR Code

	Diese Methode ist stabiler. Und sie reduziert die Komplexität und sie erlaubt: Mehr Bilder pro Sekunde zu verarbeiten. Folglich werden wir uns wahrscheinlich diese Methode einsetzen am Wettbewerb. Es ist aber nicht so, dass wir die andere Art, also Erkennung der Topfpflanze (wie im Video gezeigt) komplett vergessen. Wir werden diese Idee im Hinterkopf behalten. Und natürlich ist es praktisch, einen Plan B zu haben. Sollte sich herausstellen, dass die Erkennung des QR Codes als Object nicht funktionerit 


Die tatsächliche Art der Pflanze ist in diesem ersten Schritt noch nicht relevant.  


Wir verwenden ein Objekterkennungsmodel, welches unter anderem auf diese Klassen ausgerichtet ist. 
Sobald eine Pflanze entdeckt wird, passieren drei Dinge. 
- Bluetooth: Mikrokontroller bekommt das Signal, anzuhalten. 
- Bild der Pflanze auf den Webserver schicken.
- Qr Code Information Lesen und speichern. 


Sobald alle Threads fertig sind, kann weiter gefahren werden. Diese dreiteilige Prozedur, wenn man so will, wir Nebenläufig realisiert. 


----Der erste Weg -----
Das App teilt dem Mikrocontroller mit: "Hey! Ich habe eine Pflanze entdeckt. Wir müssen kurz anhalten. Die Mitteilung erfolgt innerhalb weniger Millisekdungen. Die Bluetooth Verbindung ist während der ganzen Fahrt aktiv. Nach dem Anhalten Signal kann das Fahrzeug natürlich nicht direkt weiter machen, man muss daran denken, dass es einen Bremsweg gibt.
Speichern ein Bild der Planze. 
Der QR Code wird gelesen. Beide diese Informationenen werden auf den Webserver geschickt. 
Das ist jetzt eine technische Frage: Wie wird Übermittlung von Informationen auf den Webserver realisiert? 


----Der zweite Weg-----

1.) Wenn ein QR Code detektiert wird, started das Hauptprogramm. Wichtig: Hier ist gemeint, die QR Code Erkennung als Objekt. In anderen Worten: Die Erkennung des QR-Codes als solches, und erst in einem zweiten Schritt wird der QR Code gelesen. 



## Webserver

Kurz erklären: Ubuntu Webserver: Ein einzelnes Docker Image, das deployed wird. 

Hier: Demo Logs und Demo Bilder. Nach der Demo des Logging: Was ist jetzt hier passiert? 
1.) Das App hat eine Verbindung auf den Webserver aufgebaut. 
2.) Der Webserver akzeptiert die Verbindung. (Merkt sich die ID, um das App auch als Client identifizieren zu können)
3.) Jetzt ist die Vebindung offen. Das heisst, wir haben einen Kommunikationskanal, in welchem wir in beide Richtungen Daten senden können. 
4.) Das App schickt periodisch Text-basierte Nachrichten und Bilder. Der Webserver akzeptiert diese und sendet sie an alle Clients weiter. Das hat den Effekt, dass neue Nachrichten erscheinen, ohne dass die Seite neu geladen werden muss.   


## Entscheid Option 2

Option 2 ist unser Favorit. 
### KISS
Ein sehr bekanntes Software design Prinzip ist KEEP IT SIMPLE. Das ist eigentlich fast eine Binsensweisheit. Der Programmieren hat gut daran, wenn er jeden Aspekt des Sytems so simpel wie möglich haltet.
Nicht nur gibt das weniger Möglichkeiten für Bugs. Komplexität wird auhc reduziert. Und Komplexität ist der verlangsamende Faktor im Software entwicklungsprozess. 
# FPS
Tests haben ergeben, dass die Lösung, die nur den QR Code erkennt, deutlich effizienter ist. Effizienz ist definiert als die Arbeit pro Zeiteinheit. Und mit der QR-Code Lösung können mehr Bilder verarbeitet werden. 
# Schneller fahren
Als direkte Folge der vorherigen Aussage: Wir können schneller fahren, weil die Verarbeitungsgeschwindigkeit der Bilderkennung höhöer ist. Das freut uns natürlich. Wir wollen so schnell wie möglich sein. 


# Webserver






## Probleme

Ein immer wieder kommendes "Problem", wenn man so will, ist information overload. Das betrifft in erster Linie das Programmieren. Für jedes kleine Subproblem gibt es in der Regel zehn verschienene Wege, es zu lösen. Es gibt Lösungen wie Sand am Mehr. Oft gibt es keinen einfachen Test, zum eine Lösung von einer anderen zu unterscheiden. Und es kann natürlich vorkommen, dass beide Lösungen implemntiert werden müssen, bis man weiss, welche der beidenn die Bessere ist. 
### Android
Android ist eine komplexe Platoform. Das Android Ökosystem ist enorm gewachsen in den letzten paar Jahren. Es hat eine gewisse Lernkurve gegeben am Anfang. 

# Android
Android ist eine komplexe Platoform. Das Android Ökosystem ist enorm gewachsen in den letzten paar Jahren. Es hat eine gewisse Lernkurve gegeben am Anfang. 


# Zusammenfassung
 
Einiges ist schon fertig gestellt. So funktioniert zum Beispiel die Pfaderkennung schon gut und das Fahrzeug korrigiert seine Fahrtrichtung, wenn es eine Kurve gibt. 

Für die Zukunft planen wir vor allem, viele manuelle Tests zu machen. Je komplexer ein System ist, desto höher ist die Wahrscheinlichkeit dass plötzlich ein Modul nicht so funktioniert, wie es gedacht war. Man sieht erst ob ein wirklich funktioniert, wenn man alle Teilelemente zusammensetzt. 