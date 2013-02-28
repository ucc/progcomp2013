/**
 * @class Agent
 * @purpose Class that represents an agent which will play qchess
 */

import java.util.Random;
import java.util.Vector;

class Agent
{
	public Agent(String colour) throws Exception
	{
		this.colour = Piece.str2colour(colour);

		this.board = new Board();
		this.selected = null;
		this.rand = new Random();
	}

	public static void main(String [] args)
	{
		String colour = Reader.readLine();
		
		try
		{
			Agent agent = new Agent(colour);
			agent.Run();
		}
		catch (Exception e)
		{
			//System.err.println("EXCEPTION: agent.Run - "+e); 
			e.printStackTrace();
		}
	}

	public void Run() throws Exception
	{
		while (true)
		{
			Vector<String> v = Reader.readTokens();
			
			String cmd = v.get(0);
			
			if (cmd.compareTo("QUIT") == 0)
				break;
			else if (cmd.compareTo("SELECTION?") == 0)
			{
				Square s = select();
				System.out.println(Integer.toString(s.x) + " " + Integer.toString(s.y));
			}
			else if (cmd.compareTo("MOVE?") == 0)
			{
				Square s = move();
				System.out.println(Integer.toString(s.x) + " " + Integer.toString(s.y));
			}
			else
			{
				int x = Integer.parseInt(v.get(0));
				int y = Integer.parseInt(v.get(1));
				if (v.get(2).compareTo("->") == 0)
				{
					int x2 = Integer.parseInt(v.get(3));
					int y2 = Integer.parseInt(v.get(4));
					board.Update_move(x, y, x2, y2);
				}
				else
				{
					int index = Integer.parseInt(v.get(2));
					String type = v.get(3);
					board.Update_select(x, y, index, type);
				}
			}
		}
	}
		
	public Square select() throws Exception
	{
		Vector<Piece> p = board.pieces(colour);
		int choice = rand.nextInt(p.size());
		Square s = board.Get_square(p.get(choice).x, p.get(choice).y);
		if (s.piece == null)
			throw new Exception("ARGH");
		selected = s.piece;
		return s;
	}

	public Square move()
	{
		Vector<Square> v = new Vector<Square>();
		board.Get_moves(selected, v);
		return v.get(rand.nextInt(v.size()));
	}
	
	private final Piece.Colour colour; // colour of the agent; do not change it
	private Board board;
	private Piece selected; 
	private Random rand;
		
};
