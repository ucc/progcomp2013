/**
 * @file Piece.java
 * @purpose Represent Quantum Chess Piece
 * @author Sam Moore (matches@ucc.asn.au)
 */



/**
 * @class Piece
 * @purpose Represent a quantum chess piece
 */
public class Piece
{
		public enum Type {PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING, UNKNOWN};
		public enum Colour {WHITE, BLACK};

		public Piece(int new_x, int new_y, Colour new_colour, Type type1, Type type2)
		{
			this.x = new_x;
			this.y = new_y;
			this.colour = new_colour;
			this.types = new Piece.Type[2];
			this.types[0] = type1;
			this.types[1] = type2;
			this.type_index = -1;
		}

		public Piece(Piece cpy)
		{
			this.x = cpy.x;
			this.y = cpy.y;
			this.colour = cpy.colour;
			this.types[0] = cpy.types[0];
			this.types[1] = cpy.types[1];
			this.type_index = cpy.type_index;
		}

		public int x; 
		public int y; // position of the piece
		public Piece.Colour colour; // colour of the piece
		public int type_index; // indicates state the piece is in; 0, 1, or -1 (unknown)
		public Piece.Type[] types; // states of the piece
		public Piece.Type current_type; // current state of the piece
		
		public static Piece.Type str2type(String str) throws Exception
		{
			if (str.compareTo("king") == 0)
				return Piece.Type.KING;
			else if (str.compareTo("queen") == 0)
				return Piece.Type.QUEEN;
			else if (str.compareTo("rook") == 0)
				return Piece.Type.ROOK;
			else if (str.compareTo("bishop") == 0)
				return Piece.Type.BISHOP;
			else if (str.compareTo("knight") == 0)
				return Piece.Type.KNIGHT;
			else if (str.compareTo("pawn") == 0)
				return Piece.Type.PAWN;
			else if (str.compareTo("unknown") == 0)
				return Piece.Type.UNKNOWN;

			throw new Exception("Piece.str2type - string " + str + " isn't a valid type");
				
		}
		public static Piece.Colour str2colour(String str) throws Exception
		{
			if (str.compareTo("white") == 0)
				return Piece.Colour.WHITE;
			else if (str.compareTo("black") == 0)
				return Piece.Colour.BLACK;
			

			throw new Exception("Piece.str2colour - string " + str + " isn't a valid colour");
		}
}

