/**
 * @class Square
 * @purpose Represent a Square on the board; not necessarily occupied
 */
public class Square
{
	public Square(int new_x, int new_y, Piece new_piece)
	{
		this.x = new_x; 
		this.y = new_y; 
		this.piece = new_piece;
	}
	public	Square(Square cpy)
	{
		this.x = cpy.x;
		this.y = cpy.y;
		this.piece = cpy.piece;
	}
	public	int x;
	public int y; // position of the square
	public	Piece piece; // Piece that is in the Square (null if unoccupied)
};
