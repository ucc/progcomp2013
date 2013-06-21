/**
 * qwebchess.js
 * jQuery interface for Quantum Chess
 *
 * @authors Sam Moore and Mitch Pomery
 */

pieceSelected = ""; // currently selected piece
playerColour = ""; // colour of this player

// Unicode representations of chess pieces
pieceChar = {"W" : { "p" : "\u2659", "h" : "\u2658", "b" : "\u2657", "r" : "\u2656", "q" : "\u2655", "k" : "\u2654", "?" : "?"},
	     "B" : { "p" : "\u265F", "h" : "\u265E", "b" : "\u265D", "r" : "\u265C", "q" : "\u265B", "k" : "\u265A", "?" : "?"}};

emptyHTML = "<!--0-->&nbsp; <big> <bold>&nbsp;</bold> </big> &nbsp;"

gameStarted = false;
canClick = true;

// jQuery foo goes in here
$(document).ready(function()
{
	// Click the start/quit button
	$("#start").click(function() 
	{
		if (gameStarted === false)
		{
			gameStarted = true;
			$("#board").boardLoad();
			$("#welcome").hide();
			$("#status").show();
			$("#status").html("white SELECT?");
			$("#start").html("Quit Game");
			pieceSelected = "";
			canClick = false;
			$.ajax({url : "/cgi-bin/qchess.cgi", data : {r : "force_quit"}, success : function() {}});
			$.ajax({url : "/cgi-bin/qchess.cgi", data : {r : "start", m : "black"}}).done(function(data) {$(this).update(data)});
		
				
		}
		else
		{
			gameStarted = false;
			$("#welcome").show();
			$("#status").html("Game over");
			$("#start").html("New Game");
			canClick = false;
			$.ajax({url : "/cgi-bin/qchess.cgi", data : {r : "quit"}, success : function() {console.log("Quit game");}});
		}
	});

	// bind click event to table cells
	$("#board").on('click', 'td' , function(e)
	{
		if (canClick === false)
			return;
	
		var id = $(this).attr("id");	
		legal = true;
		if (pieceSelected === "")
		{
			if ($(this).legalSelection())
			{
				pieceSelected = id;
				$(this).setSquareColour("blue");
			}
			else
			{
				legal = false;
				alert("Illegal selection " + id);
			}
		}
		else
		{
			mover = $("#board").find("#"+pieceSelected);
			if (mover.legalMove($(this)))
			{
				$("#status").html(colourString(otherColour(mover.getColour())) + " SELECT?");
				mover.move($(this));
				pieceSelected = "";
				$("#board td").each(function() {$(this).setSquareColour("default");});
			}
			else
			{
				legal = false;
				alert("Illegal move " + id);
			}
		}
		
		if (legal)
		{
			canClick = false;
			$.ajax({url : "/cgi-bin/qchess.cgi", data : {x : id[0], y : id[1]}}).done(function(data) {$(this).update(data)});
		}
	});

	$.fn.showMoves = function()
	{
		$(this).setSquareColour("green");
		var that = $(this); //Look [DJA]! I used it!
		$("#board td").each(function()
		{
			if (that.legalMove($(this)) === true) // See?
			{
				//alert("Legal move from " + that.attr("id") + " -> " + $(this).attr("id"));
				$(this).setSquareColour("red");
			}
		});
		
	}

	// Get colour of occupied square
	// W - white
	// B - black
	// 0 - unoccupied
	$.fn.getColour = function()
	{
		return $(this).html()[4]; // yeah, I know this is horrible, so sue me
	}

	// Get type of piece
	$.fn.getType = function()
	{
		return $(this).html().match(/<bold>(.*)<\/bold>/)[1]; // again, I know it's horrible, so sue me
	}

	// Get coords
	$.fn.getX = function() {return Number($(this).attr("id")[0]);}
	$.fn.getY = function() {return Number($(this).attr("id")[1]);}
	
	// Check a square is a valid selection
	$.fn.legalSelection = function()
	{
		return ($(this).getColour() == playerColour);
	}

	// determine whether a piece can move into another square
	$.fn.legalMove = function(target)
	{
		if (target.getColour() == $(this).getColour())
			return false;
		if (target.getX() == $(this).getX() && target.getY() == $(this).getY())
			return false;
		switch ($(this).getType())
		{
			case pieceChar["W"]['p']:
				if ($(this).getY() == 6 && target.getY() == 4 && $(this).getX() == target.getX() && target.getColour() == '0')
					return true;
				if ($(this).getY() - target.getY() != 1 || Math.abs($(this).getX() - target.getX()) > 1)
					return false;
				return ($(this).getX() == target.getX() || target.getColour() != '0');

			case pieceChar["B"]['p']:
				if ($(this).getY() == 1 && target.getY() == 3 && $(this).getX() == target.getX())
					return true;
                                if ($(this).getY() - target.getY() != -1 || Math.abs($(this).getX() - target.getX()) > 1)
	                                return false;
                                return ($(this).getX() == target.getX() || target.getColour() != '0');

			case pieceChar["W"]['h']:
			case pieceChar["B"]['h']:
				return ((Math.abs($(this).getY() - target.getY()) == 2 && Math.abs($(this).getX() - target.getX()) == 1)
					|| (Math.abs($(this).getX() - target.getX()) == 2 && Math.abs($(this).getY() - target.getY()) == 1));

			case pieceChar["W"]['k']:
			case pieceChar["B"]['k']:
				return (Math.abs($(this).getX() - target.getX()) <= 1 && Math.abs($(this).getY() - target.getY()) <= 1);
			case pieceChar["W"]['b']:
			case pieceChar["B"]['b']:
				//console.log("" + Math.abs($(this).getX() - target.getX()) + " vs " + Math.abs($(this).getY() - target.getY()));
				if (Math.abs($(this).getX() - target.getX()) != Math.abs($(this).getY() - target.getY()))
					return false;
				break;
			case pieceChar["W"]['r']:
			case pieceChar["B"]['r']:
				//console.log("" + Math.abs($(this).getX() - target.getX()) + " vs " + Math.abs($(this).getY() - target.getY()));
				console.log("Rook");
				if (Math.abs($(this).getX() - target.getX()) != 0 && Math.abs($(this).getY() - target.getY()) != 0)
					return false;
				break;
			case pieceChar["W"]['q']:
			case pieceChar["B"]['q']:
				//console.log("" + Math.abs($(this).getX() - target.getX()) + " vs " + Math.abs($(this).getY() - target.getY()));
				if (Math.abs($(this).getX() - target.getX()) != Math.abs($(this).getY() - target.getY()))
				{
					if (Math.abs($(this).getX() - target.getX()) != 0 && Math.abs($(this).getY() - target.getY()) != 0)
						return false;
				}
				break;
			default:
				return false;
		}
		console.log("scanning");
		var vx = ($(this).getX() == target.getX()) ? 0 : (($(this).getX() < target.getX()) ? 1 : -1);
		var vy = ($(this).getY() == target.getY()) ? 0 : (($(this).getY() < target.getY()) ? 1 : -1);
		var x = $(this).getX() + vx; var y = $(this).getY() + vy;
		while ((x != target.getX() || y != target.getY()) && x >= 0 && y >= 0 && x < 8 && y < 8)
		{
			var c = $("#"+x+""+y).getColour();
			if (c === "W" || c === "B")
			{
				console.log("Blocked at "+x+""+y);
				return false;
			}
			else
				console.log("Scan ok at "+x+""+y);
			x += vx;
			y += vy;			
		}	
		return true;
	}

	// Move square to another
	$.fn.move = function(dest)
	{
		dest.html($(this).html());
		$(this).html(emptyHTML);

		// Collapse into quantum state if on a black square
		if ((dest.getX() + dest.getY()) % 2 != 0 && (dest.html()[0] == '?' || dest.html()[dest.html().length-1] != dest.html()[0]))
		{
			oldHTML = dest.html();
			dest.html(oldHTML.replace(/<bold>.*<\/bold>/i, "<bold>?</bold>"));
		}
	}

	// Interpret AJAX response
	$.fn.update = function(data)
	{
		console.log("AJAX Response:\n"+data);
		var lines = data.split("\n");
		var timeout = false;
		for (var i = 0; i < lines.length; ++i)
		{
			var tokens = lines[i].split(" ");

			if (!isNaN(tokens[0]) && !isNaN(tokens[1]))
			{
				s1 = $("#board").find("#"+tokens[0]+tokens[1])
				if (tokens[2] === "->")
				{
					if (s1.html()[4] != '0')
					{
						s2 = $("#board").find("#"+tokens[3]+tokens[4]);
						timeout = true;
						setTimeout((function(x) 
						{
							return function() 
							{
								s1.move(x);
								$("#board td").each(function() {$(this).setSquareColour("default");});
								x.setSquareColour("blue");
								setTimeout((function(xx) 
								{
									return function() 
									{
										xx.setSquareColour("default"); canClick = true;
										$("#status").html(colourString(playerColour) + " SELECT?");
									};
								}(x)), 500);
							};
						}(s2)), 500);
					}
				}
				else if (tokens.length === 4 && !isNaN(tokens[2]) && isNaN(tokens[3]))
				{
					var t = "h";
					if (tokens[3] != "knight")
						t = tokens[3][0];
			
					var oldHTML = s1.html();
					var c = s1.getColour();
					if (tokens[2] == "1")
					{
						oldHTML = oldHTML.substring(0, oldHTML.length-1)+pieceChar[c][t];
					}
					s1.html(oldHTML.replace(/<bold>.*<\/bold>/i, "<bold>"+pieceChar[c][t]+"</bold>"));
					//console.log(oldHTML + " ==> " + s1.html());
					s1.setSquareColour("green");
					s1.showMoves();
					$("#status").html(colourString(s1.getColour()) + " MOVE?");
					
				}
			}
			else switch (lines[i])
			{
	
				case "SELECT?":
					pieceSelected = "";
				case "MOVE?":
				case "":
				case "New game.":
					break;
				case "START white":
					if (playerColour == "")
					{
						playerColour = "W";
						break;
					}
				case "START black":
					if (playerColour == "")
					{
						playerColour = "B";
						break;
					}
				default:
					alert("Game ends: " + lines[i]);
					gameStarted = false;
					$("#start").html("New Game");
					$("#status").html("Game over");
					//$("#board").html("");
					
					
					break;
			}
		}
		if (timeout == false)
			canClick = true;
	}

	//Reset the colour of a square
	$.fn.setSquareColour = function(type)
	{
		var colour = "000000";
	        switch (type)
        	{
	                case "blue":
                	        colour = "5555aa";
        	                break;
			case "green":
				colour = "55aa55";
				break;
			case "red":
				colour = "aa5555";
				break;
	                default:
                	        colour = "aaaaaa";
        	                break;
	        }

	        id = $(this).attr("id");
        	if ((Number(id[0]) + Number(id[1])) % 2 == 0)
	        {	
        	        colour = addHexColour(colour, "555555");
	        }
        	$(this).css("background-color", "#"+colour);
	}

	// Loads the board
	$.fn.boardLoad = function()
	{
        	boardHTML = "";
	        for (var y = 0; y < 8; ++y)
	        {
                	boardHTML += "<tr id=\"y"+y+"\">";
        	        for (var x = 0; x < 8; ++x)
	                {
                        	boardHTML += "<td id=\""+x+""+y+"\">"+emptyHTML+"</td>";
                	}
        	        boardHTML += "</tr>";
	        }
        	$(this).html(boardHTML);

	        $(this).find("td").each(function()
        	{
	                $(this).setSquareColour("default");
	        });

		// Add pieces
		for (var x = 0; x < 8; ++x)
		{
			// pawns
			$(this).find("#"+x+"1").html("<!--B--> "+pieceChar["B"]["p"]+"<big> <bold>?</bold> </big> ?");
			$(this).find("#"+x+"6").html("<!--W--> "+pieceChar["W"]["p"]+"<big> <bold>?</bold> </big> ?");
		
			t = "?";
			switch (x)
			{
				case 0:
				case 7:
					t = 'r';
					break;
				case 1:
				case 6:
					t = 'h';
					break;
				case 2:
				case 5:
					t = 'b';
					break;
				case 4:
					t = 'q';
					break;
			}
			if (x == 3)
				continue;
			$(this).find("#"+x+"0").html("<!--B--> "+pieceChar["B"][t]+"<big> <bold>?</bold> </big> ?");
			$(this).find("#"+x+"7").html("<!--W--> "+pieceChar["W"][t]+"<big> <bold>?</bold> </big> ?");
		}
		t = pieceChar["B"]["k"];
		$(this).find("#30").html("<!--B--> "+t+"<big> <bold>"+t+"</bold> </big> "+t);
		t = pieceChar["W"]["k"];
                $(this).find("#37").html("<!--W--> "+t+"<big> <bold>"+t+"</bold> </big> "+t);
		
	}

});


// Add two hex colours
function addHexColour(c1, c2) 
{
  var hexStr = (parseInt(c1, 16) + parseInt(c2, 16)).toString(16);
  while (hexStr.length < 6) { hexStr = '0' + hexStr; } // Zero pad.
  return hexStr;
}

function colourString(c)
{
	return (c == "W") ? "white" : "black";
}

function otherColour(c)
{
	return (c == "W") ? "B" : "W";
}
