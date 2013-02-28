/**
 * @class Board
 * @purpose Represent a quantum chess board
 */

import java.util.Vector;

class Board
{
	public static final int WIDTH = 8;
	public static final int HEIGHT = 8;
	public	Board()
	{
	
		this.grid = new Square[Board.WIDTH][Board.HEIGHT];
		for (int x = 0; x < Board.WIDTH; ++x)
		{
			for (int y = 0; y < Board.HEIGHT; ++y)
			{
				this.grid[x][y] = new Square(x, y, null);
				this.grid[x][y].x = x;
				this.grid[x][y].y = y;
			}
		}
		Piece.Colour[] colours = {Piece.Colour.BLACK, Piece.Colour.WHITE};
		
		this.white = new Vector<Piece>();
		this.black = new Vector<Piece>();
		for (int i = 0; i < colours.length; ++i)
		{
			Vector<Piece> p = pieces(colours[i]);
			
			// add pawns
			int y = (i == 0) ? 1 : Board.HEIGHT-2;
			for (int x = 0; x < Board.WIDTH; ++x)
			{	
				p.add(new Piece(x, y, colours[i], Piece.Type.PAWN, Piece.Type.UNKNOWN));
			}

			// add major pieces
			y = (i == 0) ? 1 : Board.HEIGHT-1;
			
			p.add(new Piece(0, y, colours[i], Piece.Type.ROOK, Piece.Type.UNKNOWN));
			p.add(new Piece(1, y, colours[i], Piece.Type.KNIGHT, Piece.Type.UNKNOWN));
			p.add(new Piece(2, y, colours[i], Piece.Type.BISHOP, Piece.Type.UNKNOWN));
			Piece k = new Piece(3, y, colours[i], Piece.Type.KING, Piece.Type.KING);
			p.add(k);
			if (i == 0)
				white_king = k;
			else
				black_king = k;
			p.add(new Piece(4, y, colours[i], Piece.Type.QUEEN, Piece.Type.UNKNOWN));
			p.add(new Piece(5, y, colours[i], Piece.Type.BISHOP, Piece.Type.UNKNOWN));
			p.add(new Piece(6, y, colours[i], Piece.Type.KNIGHT, Piece.Type.UNKNOWN));
			p.add(new Piece(7, y, colours[i], Piece.Type.ROOK, Piece.Type.UNKNOWN));
		
			for (int j = 0; j < p.size(); ++j)
			{
				Piece pp = p.get(j);
				grid[pp.x][pp.y].piece = pp;
			}
			
		}
		
	}


	public	Vector<Piece> pieces(Piece.Colour colour) 
	{
		return ((colour == Piece.Colour.WHITE) ? white : black);
	}	
	public	Piece king(Piece.Colour colour) 
	{
		return ((colour == Piece.Colour.WHITE) ? white_king : black_king);
	}
		
	public	void Update_move(int x, int y, int x2, int y2)
	{
		Square s1 = grid[x][y];
		Square s2 = grid[x2][y2];
		if (s2.piece != null)
		{
			Vector<Piece> v = pieces(s2.piece.colour);
			v.remove(s2.piece);
			
			if (s2.piece == king(s2.piece.colour))
			{
				if (s2.piece.colour == Piece.Colour.WHITE)
					white_king = null;
				else
					black_king = null;
			}
		}
		
		s1.piece.x = x2;
		s1.piece.y = y2;
		s2.piece = s1.piece;
		s1.piece = null;
	}
	public	void Update_select(int x, int y, int index, String type) throws Exception
	{
		Square s = grid[x][y];
		s.piece.type_index = index;
		s.piece.types[index] = Piece.str2type(type);
		s.piece.current_type = s.piece.types[index];
		
	}
	
	public	Square Get_square(int x, int y) 
	{
		return grid[x][y]; // get square on board
	}

	public void Get_moves(Piece p, Vector<Square> v)
	{
		int x = p.x; 
		int y = p.y;
		if (p.current_type == Piece.Type.KING)
		{
			Move(p, x+1, y, v);
			Move(p, x-1, y, v);
			Move(p, x, y+1, v);
			Move(p, x, y-1, v);
			Move(p, x+1, y+1, v);
			Move(p, x+1, y-1, v);
			Move(p, x-1, y+1, v);
			Move(p, x-1, y-1, v);
		}
		else if (p.current_type == Piece.Type.KNIGHT)
		{
			Move(p, x+2, y+1, v);
			Move(p, x+2, y-1, v);
			Move(p, x-2, y+1, v);
			Move(p, x-2, y-1, v);
			Move(p, x+1, y+2, v);
			Move(p, x-1, y+2, v);
			Move(p, x+1, y-2, v);
			Move(p, x-1, y-2, v); 
		}
		else if (p.current_type == Piece.Type.PAWN)
		{
			int y1 = (p.colour == Piece.Colour.WHITE) ? Board.HEIGHT-2 : 1;
			int y2 = (p.colour == Piece.Colour.WHITE) ? y1 - 2 : y1 + 2;
			if (p.types[0] == Piece.Type.PAWN && p.y == y1)
			{
				
				Move(p, x, y2, v);
			}
			y2 = (p.colour == Piece.Colour.WHITE) ? y - 1 : y + 1;
			Move(p, x, y2, v);
	
			if (Valid_position(x-1, y2) && grid[x-1][y2].piece != null)
				Move(p, x-1, y2, v);
			if (Valid_position(x+1, y2) && grid[x+1][y2].piece != null)
				Move(p, x+1, y2, v);
		}
		else if (p.current_type == Piece.Type.BISHOP)
		{
			Scan(p, 1, 1, v);
			Scan(p, 1, -1, v);
			Scan(p, -1, 1, v);
			Scan(p, -1, -1, v);
		}
		else if (p.current_type == Piece.Type.ROOK)
		{
			Scan(p, 1, 0, v);
			Scan(p, -1, 0, v);
			Scan(p, 0, 1, v);
			Scan(p, 0, -1, v);
		}
		else if (p.current_type == Piece.Type.QUEEN)
		{
			Scan(p, 1, 1, v);
			Scan(p, 1, -1, v);
			Scan(p, -1, 1, v);
			Scan(p, -1, -1, v);
			Scan(p, 1, 0, v);
			Scan(p, -1, 0, v);
			Scan(p, 0, 1, v);
			Scan(p, 0, -1, v);
		}

	}

	// determine if position is on the board
	public boolean Valid_position(int x, int y) 
	{
		return (x >= 0 && x <= Board.WIDTH-1 && y >= 0 && y <= Board.HEIGHT-1);
	}

	private Square[][] grid;

	
	private Vector<Piece> white;
	private Vector<Piece> black;
	private Piece white_king;
	private Piece black_king;

		// Add a move to the vector if it is valid
	private void Move(Piece p, int x, int y, Vector<Square> v)
	{
		if (Valid_position(x, y) && (grid[x][y].piece == null || grid[x][y].piece.colour != p.colour))
		{
			v.add(grid[x][y]);
		}
	}

		// Add all valid moves in a direction, stopping at the first invalid move
	private void Scan(Piece p, int vx, int vy, Vector<Square> v)
	{
		int x = p.x + vx;
		int y = p.y + vy;
		while (Valid_position(x, y) && (grid[x][y].piece == null || grid[x][y].piece.colour != p.colour))
		{
			v.add(grid[x][y]);
			
			if (grid[x][y].piece != null)
				break;
			x += vx;
			y += vy;
		}
	}
}

