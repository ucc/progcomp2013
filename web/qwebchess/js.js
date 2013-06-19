//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?r=start
//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?r=quit
//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?x=X&y=Y (0 indexed)

pieceSelected = ""; // currently selected piece
piece = "";
colour = "W"; // colour of this player

// Unicode representations of chess pieces
pieceChar = {"W" : { "p" : "\u2659", "h" : "\u2658", "b" : "\u2657", "r" : "\u2656", "q" : "\u2655", "k" : "\u2654", "?" : "?"},
	     "B" : { "p" : "\u265F", "h" : "\u265E", "b" : "\u265D", "r" : "\u265C", "q" : "\u265B", "k" : "\u265A", "?" : "?"}};

// Select (or move) a piece
function selectPiece(loc) {
	x = (""+loc).charAt(1);
	y = (""+loc).charAt(0);
	//alert(loc);

	// work out whether to select or move based on the comment tag for the clicked location
	// It is either "<!--W-->" (white; select) or <!--B-->" (black) or "<!--0-->" (empty)
	if (pieceSelected == "") {
		if (document.getElementById(loc).innerHTML.charAt(4) == colour) {
			console.log("Piece Selected: " + loc);
			pieceSelected = loc;
			ajaxUpdate("x=" + x + "&y=" + y);
		}
	}
	else {
		//alert("pieceMoved");
		if (validMove(pieceSelected, piece, loc)) {
			doMove(pieceSelected, loc);
			ajaxUpdate("x=" + x + "&y=" + y);
			pieceSelected = "";
		}
		else {
			console.log("Invalid Move");
		}
	}
}

function validMove(start, piece, end) {
	return true;
}

function doMove(start, end) {
	begin = document.getElementById(start);
	end = document.getElementById(end);
	htmlToMove = begin.innerHTML;
	end.innerHTML = htmlToMove;
	begin.innerHTML = "<!--0--> <p>&nbsp;</p>";

	if (end[end.length-1] % 2 == 0)
		end.innerHTML.replace(/<big>.*<\/big>/i, "<big>?</big>");
	//console.log("Piece Moved");
}

function boardLoad() {
	ajaxUpdate("r=force_quit");
	
	
	
	for (i = 0; i < 8; i++) {
		for (j = 0; j < 8; j++) {
			e = i + "" + j;
			elem = document.getElementById(e)
			if ((i + j) % 2 == 0)
				elem.style.background="#FFF";
			else
				elem.style.background="#DDD";
		}
	}
	
	//Place pieces on the board
	for (i = 0; i < 8; i++) {
		black = document.getElementById("1" + i);
		white = document.getElementById("6" + i);
		//pawns
		black.innerHTML = "<!--B--> " + pieceChar["B"]["p"] + " <big> <bold>?</bold> </big> ?";
		white.innerHTML = "<!--W--> " + pieceChar["W"]["p"] + " <big> <bold>?</bold> </big> ?";
		
		black = document.getElementById("0" + i);
		white = document.getElementById("7" + i);
		piece = "p";
		if (i == 0 || i == 7)
			piece = "r";
		if (i == 1 || i == 6)
			piece = "h";
		if (i == 2 || i == 5)
			piece = "b";
		if (i == 3)
			piece = "k";
		if (i == 4)
			piece = "q";
		//major pieces
		black.innerHTML = "<!--B--> " + pieceChar["B"][piece] + "<big> <bold>?</bold> </big> ?";
		white.innerHTML = "<!--W--> " + pieceChar["W"][piece] + "<big> <bold>?</bold> </big> ?";

		// empty squares
		for (j = 2; j < 6; j++)
		{
			square = document.getElementById(""+j + i);
			square.innerHTML = "<!--0--> <p>&nbsp;</p>";
		}
	}
	
	setTimeout(function(){ajaxUpdate("r=start");}, 1000);
}

//AJAX Stuff
function ajaxUpdate(queryString) {
	var ajaxRequest;  // The variable that makes Ajax possible!

	try {
		// Opera 8.0+, Firefox, Safari
		ajaxRequest = new XMLHttpRequest();
	} catch (e) {
		// Internet Explorer Browsers
		try {
			ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
		} catch (e) {
			try {
				ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
			} catch (e) {
				// Something went wrong
				alert("Your Browser is not Ajax Compatible, Please Upgrade to Google Chrome.");
				return false;
			}
		}
	}
	
	//alert(queryString);
	
	// Create a function that will receive data sent from the server
	ajaxRequest.onreadystatechange = function () 
	{
		//alert("RS" + ajaxRequest.readyState);
		if (ajaxRequest.readyState == 4) {
			console.log("AJAX Response: " + ajaxRequest.responseText);
			lines = ajaxRequest.responseText.split("\n");

			for (var i = 0; i < lines.length; ++i)
			{
				tokens = lines[i].split(" ")

				if (isNaN(tokens[0]) || isNaN(tokens[1]))
					continue;

				pieceSelected = ""+tokens[1]+""+tokens[0];
                                square = document.getElementById(pieceSelected);
                                html = square.innerHTML;
				c = html.charAt(4);
				if (tokens[2] == "->" && document.getElementById(""+tokens[4] + "" + tokens[3]).innerHTML.charAt(4) != colour)
				{
					doMove(""+tokens[1] + "" + tokens[0], ""+tokens[4] + "" + tokens[3]);
				}
				else if (tokens.length == 4 && !isNaN(tokens[0]) && !isNaN(tokens[1]) && !isNaN(tokens[2]) && isNaN(tokens[3]))
				{
					piece = tokens[3];
					if (piece == "knight") //HACK
						piece = "h";	
					else
						piece = ""+piece.charAt(0);
					if (tokens[2] == "1")
						html[html.length-1] = pieceChar[c][piece];

					square.innerHTML = html.replace(/<big> <bold>.*<\/bold> <\/big>/i, "<big> <bold>"+pieceChar[c][piece]+"</bold> </big>");	
					console.log("innerHTML = " + square.innerHTML);
				}
			}

			/*
			if (ret.charAt(4) == "-" && ret.charAt(5) == ">") {
				//Piece has been moved
				//console.log("Moving other piece");
				lines = ret.split("\n");
				//if (lines[3] != "SELECT?") {
				if (lines[2] != "SELECT?") {
					x1 = lines[2].charAt(0);
					y1 = lines[2].charAt(2);
					x2 = lines[2].charAt(7);
					y2 = lines[2].charAt(9);
					console.log("Black Move: " + x1 + "" + y1 + " -> " + x2 + "" + y2);
					doMove(y1 + "" + x1, y2 + "" + x2);
				}
				else {
					console.log("Black Unable to move");
				}
			}
			else {
				lines = ret.split("\n");
				if (lines[1] == "MOVE?") {
					//We selected a piece
					//console.log("choose where to move our piece");
					piece = lines[0].charAt(6);
					//console.log("Piece: " + piece);
					content = document.getElementById(pieceSelected);
					contentHTML = content.innerHTML;
					//contentHTML = contentHTML.replace("?", piece);
					//"W<br /><small>p</small> <bold>?</bold> <small>?</small></span>";
					if (lines[0].charAt(4) == "1") {
						//console.log("changing quantum piece");
						contentHTML = replaceAt(contentHTML, 44, piece);
					}
					contentHTML = replaceAt(contentHTML, 28, piece);
					//console.log(contentHTML);
					//contentHTML = "CHANGED" + contentHTML;
					content.innerHTML = contentHTML;
				}
			}
			*/
			//alert(ret);
		}
	}
	
	//ar = "http://progcomp.ucc.asn.au/cgi-bin/qchess.cgi?" + queryString;
	ar = "/../../../cgi-bin/qchess.cgi?" + queryString;
	
	console.log("AJAX Request: " + ar);
	
	ajaxRequest.open("GET", ar, true);
	ajaxRequest.send();
}






function replaceAt(s, n, t) {
	//console.log(s.substring(0, n) + "\n" + t + "\n" + s.substring(n + 1) + "\n");
	return (s.substring(0, n) + t + s.substring(n + 1));
}
