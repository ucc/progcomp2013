! From the darkness of the 1970s came forth a language so foul and terrible that none can speak its name without shuddering in fear.
! And woe unto all who seek to use it, for decades of development have not dulled it's magnificent horror.

module qchess
	implicit none

	! Fortran90 doesn't have enums...
	integer, parameter :: KING=1, QUEEN=2, ROOK=3, KNIGHT=4, BISHOP=5, PAWN=6, UNKNOWN=7
	! Also it's case insensitive, but I thought I would make an effort to be consistent even if Fortran90 won't
	integer, parameter :: NONE=0, WHITE=2, BLACK=1

	integer, parameter :: BUFSIZ = 256 ! Need this for strings...

	integer, parameter :: STDERR = 0

	! But it has types! 
	type piece
		integer :: x
		integer :: y
		integer :: types(2)
		integer :: type_index
		integer :: colour
	end type piece

	! And... really... confusing... pointer... stuff
	! (You can't have an array of pointers... but you can have an array of piece_ptr)
	type piece_ptr
		type(piece), pointer :: p
	end type piece_ptr

	type board
		type(piece_ptr) :: grid(8,8)
		! If I wrote this:
		! type(piece), pointer :: grid(:,:)
		! It would be a pointer to an array of pieces... not an array of pointers to pieces
		type(piece_ptr) :: pieces(2,16)
		type(piece_ptr) :: kings(2)
	end type board

	type square
		integer :: x
		integer :: y
	end type square

	
end module qchess


program agent

	use qchess
	implicit none

	type(board) :: b

	type(square), allocatable :: moves(:)
	character(len = BUFSIZ) :: buffer
	character(len = BUFSIZ) :: buffer2
	character(len = 2) :: s
	integer :: x, y, x2, y2, i, t, colour
	real :: rand(1)


	type(piece_ptr) :: choice

	allocate(moves(0))

	call board_init(b)

	call random_seed(i) ! Probably want to fix this...
	

	read(*, '(A)') buffer
	if (buffer .eq. "white") then
		colour = WHITE
	else
		colour = BLACK
	endif
	

	
	do while (.true.)
		read(*, '(A)') buffer
		!write(STDERR,*) "Got: ", buffer
		if (buffer .eq. "QUIT black" .or. buffer .eq. "QUIT white") then
			exit
		else if (buffer .eq. "SELECTION?") then
			
			do while(.true.)
				call random_number(rand)
				i = int(rand(1) * (size(b%pieces(colour,:)) - 1)) + 1
				choice = b%pieces(colour, i)
				if (associated(choice%p)) then
					exit
				endif
			enddo		
			!write(STDERR,*) "Selected:", choice%p%x-1, choice%p%y-1
			write(*,*) choice%p%x-1, choice%p%y-1

		else if (buffer .eq. "MOVE?") then
			
			call random_number(rand)
			call possible_moves(b, choice%p, moves)

			if (size(moves) == 0) then
				!write(STDERR,*) "No moves!"
			endif

			do i=1,size(moves)
				!write(STDERR,*) "Possible move:", i, "->", moves(i)%x-1, moves(i)%y-1
			enddo
			
			i = int(rand(1) * (size(moves) - 1)) + 1

			!write(STDERR,*) "Move",i,":", choice%p%x-1, choice%p%y-1, "->", moves(i)%x-1, moves(i)%y-1
			write(*,*) moves(i)%x-1, moves(i)%y-1
			deallocate(moves)
			allocate(moves(0))
			
		else
			
			
			read(buffer, '(I2,I2, A)') x, y, buffer
			x = x + 1
			y = y + 1

			buffer2 = buffer
			read(buffer, '(A2)') s
			if (s .eq. "->") then
				read(buffer2, *) s, x2, y2
				x2 = x2 + 1
				y2 = y2 + 1
				!write(STDERR,*) "Update:", x-1, y-1, "->" , x2-1, y2-1
				call board_update_move(b, x, y, x2, y2)
			else
				read(buffer, *), i, buffer
				t = str2type(buffer)
				!write(STDERR,*) "Update:", x-1, y-1, "selected:" , i, "type:", t
				call board_update_select(b, x, y, i+1, t)
			endif
		endif

	enddo

	deallocate(moves)

	call board_destroy(b)

contains

integer function str2type(s)

	character(len=BUFSIZ), intent(in) :: s
	!write(STDERR,*) "Determine type of piece:", s, ":"
	if (s .eq. "king") then
		str2type = KING
	else if (s .eq. "queen") then
		str2type = QUEEN
	else if (s .eq. "rook") then
		str2type = ROOK
	else if (s .eq. "knight") then
		str2type = KNIGHT
	else if (s .eq. "bishop") then
		str2type = BISHOP
	else if (s .eq. "pawn") then
		str2type = PAWN
	else if (s.eq. "unknown") then
		str2type = UNKNOWN
	endif

end function str2type

subroutine piece_init(p, colour, type1, type2)

	type(piece), intent(inout) :: p
	integer, intent(in) :: colour, type1, type2
	p%colour = colour
	p%types(1) = type1
	p%types(2) = type2
	p%type_index = 0


end subroutine piece_init

subroutine board_init(b)
	type(board), intent(inout) :: b
	integer :: x, y, j
	integer :: colour

	do x=1,8
		do y=1,8
			nullify(b%grid(x,y)%p)
		enddo
	enddo

	! Add the pieces



	do colour=1,2
		j = 1
		if (colour .eq. WHITE) then
			y = 7
		else
			y = 2
		endif

		! Add pawns
		do x=1,8
			allocate(b%grid(x,y)%p)
			call piece_init(b%grid(x,y)%p, colour, PAWN, UNKNOWN)
			b%pieces(colour, j) = b%grid(x,y)
			j = j + 1
		enddo

		! Add other pieces
		if (colour .eq. WHITE) then
			y = 8
		else
			y = 1
		endif

		do x=1, 8
			allocate(b%grid(x, y)%p)
			b%pieces(colour, j) = b%grid(x,y)
			j = j + 1
		enddo
		call piece_init(b%grid(1,y)%p, colour, ROOK, UNKNOWN)
		call piece_init(b%grid(2,y)%p, colour, KNIGHT, UNKNOWN)
		call piece_init(b%grid(3,y)%p, colour, BISHOP, UNKNOWN)
		call piece_init(b%grid(4,y)%p, colour, KING, KING)
		call piece_init(b%grid(5,y)%p, colour, QUEEN, UNKNOWN)
		call piece_init(b%grid(6,y)%p, colour, BISHOP, UNKNOWN)
		call piece_init(b%grid(7,y)%p, colour, KNIGHT, UNKNOWN)
		call piece_init(b%grid(8,y)%p, colour, ROOK, UNKNOWN)

		b%kings(colour) = b%grid(4, y)
	enddo

	do x=1,8
		do y=1,8
			if (associated(b%grid(x,y)%p)) then
				b%grid(x,y)%p%x = x
				b%grid(x,y)%p%y = y
				!write(STDERR,*) "Piece", b%grid(x,y)%p%types(1), "at", x, y
			endif
		enddo
	enddo
	
end subroutine board_init

subroutine board_update_select(b, x, y, type_index, t)

	integer, intent(in) :: x, y, type_index, t
	type(board), intent(inout) :: b
	b%grid(x, y)%p%type_index = type_index
	b%grid(x, y)%p%types(type_index) = t

end subroutine board_update_select

subroutine board_update_move(b, x, y, x2, y2)

	type(board), intent(inout) :: b
	integer, intent(in) :: x, y, x2, y2
	integer :: colour, i



	if (associated(b%grid(x2, y2)%p) .eqv. .true.) then
		colour = b%grid(x2,y2)%p%colour
		do i=1,16
			if (associated(b%pieces(colour, i)%p, b%grid(x2, y2)%p)) then
				b%pieces(colour, i)%p => NULL()
			endif
		enddo
		deallocate(b%grid(x2,y2)%p)
	endif

	b%grid(x2,y2) = b%grid(x,y)
	b%grid(x,y)%p%x = x2
	b%grid(x,y)%p%y = y2
	b%grid(x,y)%p => NULL()
	


end subroutine board_update_move

subroutine possible_moves(b, p, m)

	type(board), intent(in) :: b
	type(piece), intent(in) :: p
	type(square), intent(inout), allocatable :: m(:)
	type(square), allocatable :: copy(:)
	
	integer :: i
	integer :: x, y


	

	do x=1,8
		do y=1,8
			if (legal_move(b, p, x, y) .eqv. .true.) then
				allocate(copy(size(m) + 1))
				copy(1:size(m)) = m
				deallocate(m)
				allocate(m(size(copy)))
				m(1:size(copy)) = copy
				deallocate(copy)

				m(size(m))%x = x
				m(size(m))%y = y
			else
				!write(STDERR,*) "Piece of type", p%types(p%type_index), "can't move from", p%x, p%y, "to", x, y
			endif
			
		enddo
	enddo

end subroutine possible_moves

logical function legal_move(b, p, x, y)
	
	type(board), intent(in) :: b
	type(piece), intent(in) :: p
	integer, intent(in) :: x, y


	integer :: t, c, xx, yy

	if (x .le. 0 .or. x .gt. 8 .or. y .le. 0 .or. y .gt. 8) then
		legal_move = .false.
		return
	endif

	t = p%types(p%type_index)
	c = p%colour

	!write(STDERR,*) "Test legal move for piece", p%types(p%type_index), "at", p%x-1, p%y-1, "->", x-1, y-1

	! Establish move is into empty square or takes a piece
	legal_move = .not. (associated(b%grid(x,y)%p) .and. b%grid(x,y)%p%colour .eq. c)
	if (legal_move .eqv. .false.) then
		return ! Move into allied square; not allowed
	endif


	if (t == PAWN) then
		! Check y coord
		legal_move = (c == WHITE .and. y == p%y - 1 .or. (y == p%y-2 .and. p%y == 7)) &
			.or. (c == BLACK .and. y == p%y+1 .or. (y == p%y+2 .and. p%y == 1))
		! Check x coord
		legal_move = legal_move .and. (x == p%x)
		if (legal_move .eqv. .true.) then
			! Can't move pawn forward into any occupied square
			legal_move = .not. associated(b%grid(x,y)%p)
			return
		endif
		
		if (associated(b%grid(x,y)%p) .eqv. .true.) then
			! Can take diagonally
			legal_move = (c == WHITE .and. y == p%y - 1 .and. abs(x - p%x) == 1) &
				.or. (c == BLACK .and. y == p%y+1 .and. abs(x - p%x) == 1)
		endif
			
		return
	endif
	
	if (t == KING) then
		legal_move = (abs(x - p%x) .le. 1 .and. abs(y - p%y) .le. 1)
		return
	endif
		
	if (t == KNIGHT) then
		
		legal_move = ((abs(x - p%x) == 2 .and. abs(y - p%y) == 1) &
			 .or. (abs(x - p%x) == 1 .and. abs(y - p%y) == 2))
		return 
	endif

	if (t == BISHOP .or. t == QUEEN) then
		legal_move = (abs(x - p%x) .eq. abs(y - p%y))
	endif

	if (t == ROOK .or. (t == QUEEN .and. .not. legal_move)) then
		legal_move = (abs(x - p%x) == 0 .or. abs(y - p%y) == 0)
	endif

	if (legal_move .eqv. .false.) then
		return
	endif

	xx = p%x
	yy = p%y
	do while (xx .ne. x .or. yy .ne. y)
		if (xx .gt. x) then 
			xx = xx - 1 
		endif
		if (xx .lt. x) then
			xx = xx + 1 
		endif
		if (yy .gt. y) then
			yy = yy - 1 
		endif
		if (yy .lt. y) then
			yy = yy + 1
		endif
		
		if (associated(b%grid(xx,yy)%p)) then
			legal_move = .false.
			return
		endif
	enddo



end function legal_move

subroutine board_destroy(b)
	type(board), intent(inout) :: b

	integer :: x, y, c, i

	do x=1, 8
		do y=1,8
			if (associated(b%grid(x,y)%p)) then
				deallocate(b%grid(x,y)%p)
				b%grid(x,y)%p => NULL()

			endif
		enddo
	enddo

	do c=1,2
		do i=1,16
			b%pieces(c, i)%p =>NULL()
		enddo

		b%kings(c)%p => NULL()
	enddo
	
end subroutine board_destroy



end program agent
