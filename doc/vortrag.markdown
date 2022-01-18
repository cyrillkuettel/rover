# Präentation

## App

Zuerst ganz grundsätzliche Frage: Anhalten aufgrund von QR-Code oder Pflanze?
 
Der Stand der Dinge ist, dass die Topfflanze selbst als Objekt erkannt wird.
Warum diese Entscheidung? Nun, in erster Linie gibt es schon Datensets mit genau dem Objekt, welches wir brauchen: Topfpflanzen. Um Objekterkennung zu machne, braucht man annotierte Bilder. Für QR-Codes ist es schwieriger, datensets zu finden. 
Also, basiert die Objekterkennung auf Topfpflanzen.
Die tatsächliche Art der Pflanze ist in diesem ersten Schritt noch nicht relevant.  

Das coco-dataset hat eine ganze Reihe von Klassen. Es kann mit diesem Datenset ein Modell trainiert werden. Für die Objekterkennung gibt es 80 mögliche Klassen. Praktischerweise ist eines davon "potted plant" und "vase". Das kommt sehr gelegen für uns. 

[hier noch etwas mehr über Coco präsentieren ]

Wir verwenden ein Objekterkennungsmodel, welches unter anderem auf diese Klassen ausgerichtet ist. 
Sobald eine Pflanze entdeckt wird, passieren drei Dinge. 
- Bluetooth: Mikrokontroller bekommt das Signal, anzuhalten. 
- Bild der Pflanze auf den Webserver schicken.
- Qr Code Information Lesen und speichern. 

Sobald alle Threads fertig sind, kann weiter gefahren werden. Diese dreiteilige Prozedur, wenn man so will, wir Nebenläufig realisiert. 


## Webserver


### Idee: vergleichen von Objekten. 
Schlussendlich wird eroiert, welches dieser Topfpflanzen in der Reihe, die gleiche Art ist wie die erste Pflanze. 
 
