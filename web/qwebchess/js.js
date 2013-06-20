//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?r=start
//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?r=quit
//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?x=X&y=Y (0 indexed)

pieceSelected = ""; // currently selected piece
piece = "";
colour = "W"; // colour of this player
canClick = true;

// Unicode representations of chess pieces
pieceChar = {"W" : { "p" : "\u2659", "h" : "\u2658", "b" : "\u2657", "r" : "\u2656", "q" : "\u2655", "k" : "\u2654", "?" : "?"},
	     "B" : { "p" : "\u265F", "h" : "\u265E", "b" : "\u265D", "r" : "\u265C", "q" : "\u265B", "k" : "\u265A", "?" : "?"}};

emptyHTML = "<!--0-->&nbsp; <big> <bold>&nbsp;</bold> </big> &nbsp;"

// Select (or move) a piece
function selectPiece(loc) {
	if (!canClick)
		return;

	x = (""+loc).charAt(1);
	y = (""+loc).charAt(0);
	//alert(loc);

	// work out whether to select or move based on the comment tag for the clicked location
	// It is either "<!--W-->" (white; select) or <!--B-->" (black) or "<!--0-->" (empty)
	if (pieceSelected == "") 
	{
		square = document.getElementById(loc);
		if (square.innerHTML.charAt(4) == colour) 
		{
			console.log("Piece Selected: " + loc);
			pieceSelected = loc;
			ajaxUpdate("x=" + x + "&y=" + y);
			if ((+x + +y) % 2 == 0)
				square.style.background = "#DFD";
			else
				square.style.background = "#8F8";
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

function resetColour(loc)
{
	square = document.getElementById(loc);
	if ((+loc[loc.length-1] + +loc[loc.length-2]) % 2 == 0)
		square.style.background = "#FFF";
	else
		square.style.background = "#DDD";
		
}

function validMove(start, piece, end) {
	return true;
}

function doMove(start, end) {
	alert("doMove("+start+","+end+")");
	s1 = document.getElementById(start);
	s2 = document.getElementById(end);
	s2.innerHTML = s1.innerHTML;
	s1.innerHTML = emptyHTML;

	resetColour(start);

	if ((+end[end.length-1] + +end[end.length-2]) % 2 == 1)
	{
		s2.innerHTML = s2.innerHTML.replace(/<bold>.*<\/bold>/i, "<bold>?</bold>");
	}
	//console.log("Piece Moved");
}

function boardLoad() {
	ajaxUpdate("r=force_quit");
	
	
	
	for (i = 0; i < 8; i++) {
		for (j = 0; j < 8; j++) {
			e = ""+i + "" + j;
			resetColour(e);
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
			square.innerHTML = emptyHTML;
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
				x = Number(tokens[0]);

				if (isNaN(tokens[0]) || isNaN(tokens[1]))
					continue;

                                var s1 = document.getElementById("" + tokens[1] + "" + tokens[0]);
				var s2 = document.getElementById("" + tokens[4] + "" + tokens[3]);
				if (tokens[2] == "->" && s1.innerHTML.charAt(4) != '0')
				{
					canClick = false;
					if ((+tokens[0] + +tokens[1]) % 2 == 0)
						s1.style.background = "#DFD";
					else
						s1.style.background = "#8F8";

					var doThisMove = function(start, end) {doMove(start, end); canClick = true;}(""+tokens[1]+""+tokens[0], ""+tokens[4]+""+tokens[3]);
					setTimeout(function() {doThisMove(); canClick = true;}, 500);
				}
				else if (tokens.length == 4 && !isNaN(tokens[0]) && !isNaN(tokens[1]) && !isNaN(tokens[2]) && isNaN(tokens[3]))
				{
					html = s1.innerHTML;
					c = html.charAt(4);
					piece = tokens[3];
					if (piece == "knight") //HACK
						piece = "h";	
					else
						piece = ""+piece.charAt(0);
					if (tokens[2] == "1")
						html[html.length-1] = pieceChar[c][piece];

					s1.innerHTML = html.replace(/<bold>.*<\/bold>/i, "<bold>"+pieceChar[c][piece]+"</bold>");	
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
