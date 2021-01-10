# SpeechMatE server

Il server dell'ecosistema SpeechMatE trova il senso se a valle ci sono i moduli *LaTeX editor*, *LaTeX compiler* e *PDF viewer*.

**Il progetto è un prototipo.**

Il diagramma di flusso del sistema comprensivo anche della parte client (vedi repository della [parte client](https://github.com/integr-abile/SpeechMatE_client)) è il seguente

![diagramma di flusso ad alto livello del sistema SpeechMatE](/Users/mattiaducci/Desktop/Lavoro/torinoPolin/speechmate-pipeline_texstudio/srv_processing/imgs/DiagrammaAltoLivello.png)

## Funzionamento di base

Il server esegue essenzialmente una funzione:

> ricevendo in input del testo grezzo simula degli input da tastiera di determinati tasti a seconda del testo ricevuto e dello stato attuale del sistema.

Il linguaggio matematico è rappresentabile a livello informatico/editoriale da linguaggi come MathML e LaTeX. Quest'ultimo è stato scelto come linguaggio di traduzione dell'input testuale sia per la maggiore facilità di scrittura e lettura, sia per la sua diffusione in ambito scientifico/accademico. 

Per definire in modo non ambiguo una frase qualunque e, a maggior ragione, una matematica, può non essere sufficiente analizzare una sola parola e in un flusso di parlato uno dei problemi è capire *quante* parole sono necessarie per identificare in modo non ambiguo un concetto o un elemento matematico. Per **esempio**: "più" e "più o meno". In LaTeX la loro rappresentazione è rispettivamente "+" e "\pm" ma in un flusso di parlato quando viene analizzata la parola "più", è corretto che simuli il tasto "+" della tastiera o è più corretto aspettare e vedere se le due parole successive sono "o" e "meno" e solo a quel punto decidere se simulare da tastiera "+" o i caratteri "\\" e "pm"? La seconda è l'alternativa che abbiamo scelto

## Parser 

Il funzionamento di questo server, al di là della logica di parsing del testo ricevuto, è basato sul **creare una simulazione dell'input da tastiera**: questo è il motivo per il quale dev'essere eseguito sull'host e non può essere messo all'interno di un container Docker o, più in generale, virtualizzato. Per maggiori informazioni consultare [questo link](https://github.com/moses-palmer/pynput/issues/115).

### Uso

La simulazione dell'input è proprio da immaginarsi come la pressione fisica dei tasti corrispondenti ai caratteri specificati sulla propria tastiera e l'ottica è quella di eseguire questo server in background con il programma di editing LaTeX (vedi sezione "LaTeX editor") in foreground con il cursore posizionato su un documento vuoto. Le simulazioni fatte, che da qui in poi chiamerò semplicemente *testi*, hanno un duplice scopo: essere scritte o attivare delle macro definite nell'ambiente LaTeX editor, nel nostro caso il **software Texstudio**, comunque spiegate nella sezione dedicata.

Per eseguire il server eseguire su host locale lo script `start_server.sh` (assicurati di avere la porta 5000 disponibile e non già occupata da un altro processo.. tipo un altro server Flask). Se dà problemi all'avvio installare le dipendenze python presenti in `requirements.txt` -> `pip install -r requirements.txt`. 

### Come orientarsi nel progetto

Ci sono 3 componenti principali:

- L'**entry point** è il file `main.py` nel quale avviene la ricezione delle chiamate di rete e la simulazione dell'input da tastiera. Vengono caricati file di configurazione per la parte di comandi di editing `edit_modules/json/*` e vengono gestiti ad alto livello le risposte dei layer. 
- **Layer**: lì c'è la logica del sistema. In base alla parola in ingresso il layer interroga le varie grammatiche chiedendo loro se rispondono o no ad un certo token (parola). Tiene lo stato delle varie grammatiche fino all'univocità e comunica al main cosa fare: aspettare, scrivere qualcosa, richiedere un nuovo layer. Il programma può avere più layer e ogni layer è uguale all'altro, solo ognuno viene creato con uno stato pulito. Il layer, una volta raggiunta l'univocità su cosa scrivere/comandare tra le grammatiche, comunica al main di eliminarlo, passando il controllo al layer direttamente sottostante. Questo meccanismo consente di avere una struttura ricorsiva a pila, molto comune nel linguaggio matematico. Per esempio: "3 alla seconda". "3 alla". "Alla" richiede un nuovo layer perchè potenzialmente potrei dire "3 alla terza" e via dicendo: "3 alla terza alla terza alla quarta". Nell'ultimo caso i layer sono 4: quello base e quelli riferiti alle potenze. Su un layer potrei starci di conseguenza anche molto tempo: se all'esponente ho "3x+x^2" sto per un po' su quel livello prima di creare un altro layer corrispondente alla potenza x^2. Il layer, come accennato prima, mantiene lo stato sulle grammatiche ancora "in gioco": dato che grammatiche (elementi matematici) diverse possono avere lunghezze diverse ("integrale da x a y di x alla seconda più 2" è più lunga di "y primo"), il layer deve fare da buffer in attesa che si raggiunga un accordo su cosa comunicare al main per poter essere scritto come testo. Per questo esiste un concetto di grammatiche "in gioco" e grammatiche "non in gioco". Quelle in gioco sono quelle che coi prossimi token in arrivo potrebbero metchare una loro regola, quelle non in gioco sono quelle che, dato un certo token, hanno capito che non c'è nessuna loro regola che può cominciare con quel token. Se il mio token è "integrale", la grammatica della potenza si dirà subito "non in gioco", per esempio. Il layer somministra un token alla volta alle grammatiche e per ogni token interroga tutte le grammatiche attive applicando la stessa logica alle loro risposte.
- **MathTopic**. è la classe astratta che costruisce la risposta da mandare al layer in base al match delle varie grammatiche specifiche, sottoclassi di MathTopic: esse  specificano in una libreria python che fa da wrapper a JSGF la loro struttura. Sono contenute nella cartella `math_modules`. Ad ogni regola grammaticale si aggiungono attributi (non fanno parte di JSGF, ma di python) che specificano se quella regola è una **foglia** o è un **nodo interno** (in un'ottica nella quale una grammatica è un albero). Una limitazione di questo approccio del sistema è che mantiene "poco" lo stato: una volta comunicato il testo tramite simulazione di input non si sa più cosa è stato scritto, ne si sa come ritornarci: questo perchè lo stato è contenuto in Texstudio con il quale comunichiamo avendo il cursore aperto su di lui. Per questo motivo il modo che abbiamo per scrivere un comando LaTeX complesso come "\\frac{3}{4}" è operare col cursore e mandare comandi a Texstudio di spostamento del cursore di tot posizioni, per esempio, dove "tot posizioni" è definito a livello di grammatica nel parser sapendo che regola stiamo gestendo. Diciamo che la memoria del parser è la regola tuttora in gestione più quelle "pendenti" perchè facenti parte di layer sottostanti che devono essere ancora risolti. Il movimento del cursore è determinato da attributi come `go_to_begin`, dal primo indice ritornato dal metodo `getCursorOffsetForRulename` o l'attributo `leaf_end_cursor_movement`. Ogni regola porta con se anche tutte le parole successive che possono far sì di richiamarla. Infatti ad ogni parola, come una catena, può venir metchata una regola di una certa grammatica. Queste parole successive risalgono dal layer fino al main.

In `model/enums.py` ci sono gli enumerativi che permettono di capire i concetti presenti nel progetto in termini di comunicazione di messaggi tra le componenti sopra citate.

### Scripts per texstudio

Nella cartella `scripts_texstudio` sono contenute le macro da inserire in texstudio per far sì che possa interpretare correttamente i testi/comandi inviati dal parser. Come convenzione di comunicazione con texstudio i comandi sono dei testi preceduti dal doppio underscore "__", mentre il testo può essere arbitrario e può venir intercettato da una macro di texstudio (e allora tradotto a seconda dello script), oppure lasciato scritto così com'è. Infatti non tutti i testi inviati dal parser sono frutto di match di regole: se nessuna regola viene metchata, per esempio a fronte di un "Ciao come stai?", verrà inoltrata a texstudio la stringa così com'è.

### Per creare nuove grammatiche

Basta aggiungere classi che estendono MathTopic ad uno dei file esistenti a seconda di dov'è più logico inserire l'elemento matematico che si vuole aggiungere, altrimenti creare un nuovo file in `math_modules` .py e creare lì la classe. In caso di file esistente aggiungere un'istanza della classe al metodo `generateGrammars` a fine file del modulo, altrimenti il layer non verrà considerata come grammatica. In caso di file nuovo creare un fac simile del metodo `generateGrammar` (basta che si chiami così) nella quale si istanziano  solamente le classi presenti in quel file.

### Parte di editing

Molto limitata rispetto a quella matematica, supporta comandi semplici come spostamento del cursore di tot posizioni e la sua gestione è contenuta in file di configurazione in `edit_modules/json` e in `edit_buffer.py` che contiene invece la logica di gestione dei token di editing (che arrivano sull'endpoint edit e non math) e la creazione delle risposte da tornare al main, il quale sceglie come comporre il comando da inviare a texstudio.

## LaTeX editor

### Texstudio

Software di editing latex **scriptabile** con un dialetto di EcmaScript (Qt script). Texstudio rende possibile la **creazione di macro** in 3 modi:

- Normale: dato un trigger command (testo), sostituire il testo corrispondente al comando con del testo a piacere
- Ambiente: dato un trigger command (testo), creare un ambiente `\begin{}\end{}` in base al testo inserito nella finestra di script. Per esempio: se scrivo `%itemize`, mi verrà creato un ambiente `\begin{itemize} \end{itemize}`.
- Script: L'opzione più flessibile con la quale è possibile fare tutte le due precedenti e in più è possibile compiere operazioni su editor (editing, selezione, cancellazione/aggiunta parole, movimento del cursore) o sul programma (per esempio salvare.)

**I trigger command accettano espressioni regolari.** I trigger vengono attivati scrivendo nell'editor.

Le macro sono attivabili da quello che viene scritto nell'editor e, in riferimento al parser, a ciò che il parser comunica simulando l'input. Visivamente si nota che viene scritto il testo originale e immediatamente viene sostituito con quello specificato dalla macro. 

L'unica macro che si discosta da questo ragionamento è la **macro di autosave** che non ha un comando di lancio e **dev'essere eseguita esplicitamente prima di iniziare la sessione di dettatura in modo che salvi periodicamente il file e possa dare il trigger a tutta la catena di SpeechMatE a valle.**

Per delle macro già implementate nel parser vedere la sottosezione "Scripts per texstudio" nella sezione "Parser" (sopra)

Nota: Per permettere al compilatore (esterno a texstudio) di intercettare il momento nel quale il file .tex sul quale si sta lavorando è stato modificato, è necessario che per la prima volta lo si salvi con nome



## Latex compiler

il compito di stare in ascolto di cambiamenti del file `.tex` sorgente e ricompilarlo in PDF "al volo" in una versione molto leggera in modo che la compilazione possa essere ragionevolmente detta "in tempo reale", è affidato al software [latexmk](https://mg.readthedocs.io/latexmk.html). I seguenti comandi assumono un sistema operativo UNIX (Mac/Linux)

- Configurare il funzionamento del software una volta installato

  - Su Mac installare il software di visualizzazione PDF Skim che ha la funzionalità di hot reload (quando il PDF aperto cambia si ricarica automaticamente). Su sistemi Linux cercare un PDF viewer con le stesse caratteristiche. Leggendo il contenuto di `.latexmkrc` sotto capirete perchè vi ho detto di installare Skim. 

  - andare nella home ~ e creare un file `.latexmkrc` con il seguente contenuto

  - ```
    $pdflatex = 'pdflatex -interaction=batchmode';
    $pdf_previewer = "open -a /Applications/Skim.app";
    ```

    - con $pdflatex sto dicendo a latexmk come compilare
    - con $pdf_previewer sto dicendo a latexmk che pdf viewer aprire una volta compilato il latex in PDF

- Aprire una nuova tab del terminale (sistemi UNIX) e lanciare il seguente comando `latexmk -pvc -pdf <path_file.tex>`



## PDF Viewer

Installato Skim, esso verrà aperto da Latexmk alla prima compilazione. La sua funzionalità di hot reload dovrebbe far sì che ad ogni ricompilazione, stando in ascolto dei cambiamenti del PDF, quando esso cambia, ricarichi il suo contenuto, cioè il PDF aggiornato.