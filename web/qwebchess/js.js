//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?r=start
//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?r=quit
//progcomp.ucc.asn.au/cgi-bin/qchess.cgi?x=X&y=Y (0 indexed)

pieceSelected = "";
piece = "";

function selectPiece(loc) {
	x = (""+loc).charAt(1);
	y = (""+loc).charAt(0);
	//alert(loc);
	if (pieceSelected == "") {
		if (document.getElementById(loc).innerHTML.charAt(0) == "W") {
			console.log("Piece Selected: " + loc);
			pieceSelected = loc;
			ajaxUpdate("x=" + x + "&y=" + y);
		}
	}
	else {
		//alert("pieceMoved");
		if (validMove(pieceSelected, piece, loc)) {
			ajaxUpdate("x=" + x + "&y=" + y);
			doMove(pieceSelected, loc);
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
	begin.innerHTML = "";
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
	//Pawns
	for (i = 0; i < 8; i++) {
		black = document.getElementById("1" + i);
		white = document.getElementById("6" + i);
		black.innerHTML = "B<br /><small>p</small> <bold>?</bold> <small>?</small></span>";
		white.innerHTML = "W<br /><small>p</small> <bold>?</bold> <small>?</small></span>";
		
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
		
		black.innerHTML = "B<br /><small>" + piece + "</small> <bold>?</bold> <small>?</small>";
		white.innerHTML = "W<br /><small>" + piece + "</small> <bold>?</bold> <small>?</small>";
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
	ajaxRequest.onreadystatechange = function () {
		//alert("RS" + ajaxRequest.readyState);
		if (ajaxRequest.readyState == 4) {
			console.log("AJAX Response: " + ajaxRequest.responseText);
			ret = ""+ajaxRequest.responseText;
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