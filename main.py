from flask import Flask, session, render_template, request, redirect, url_for
from random import randint

### Globals ###

app = Flask(__name__)
app.secret_key = '9*TGIKi7tggkuyUPJKdY%W^$WKLHOyjv,liIUFL>N>'

### Service / Utility Methods ###

def parsenum (s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def ttt_logic(grid, turn, color):
    rotate_grid = [[grid[0][x],grid[1][x],grid[2][x]] \
                       for x,l in enumerate(grid)]
    op_color = abs(color-3)
        
    # Handle end-game
    if turn == 9:
        for r,l in enumerate(grid):
            for c,i in enumerate(l):
                if i == 0:
                    return r,c
    # Turn 1 logic
    if turn == 1:
        non_d = randint(0,4)
        options = [(0,0),(0,2),(2,0),(2,2),(1,1)]
        return options[non_d]

    # Turn 2 logic
    if turn == 2 and grid[1][1] == 0:
        return 1,1
    elif turn == 2 and grid[1][1] > 0:
        non_d = randint(0,3)
        options = [(0,0),(0,2),(2,0),(2,2)]
        return options[non_d]
    
    # Turn 3 logic
    if turn == 3 and grid[1][1] == color:
        non_d = randint(0,3)
        options = [(0,1),(1,0),(1,2),(2,1)]
        return options[non_d]
    elif turn == 3:
        r = 0
        c = 0
        flip = randint(0,1)
        options = [(0,0),(0,2),(2,0),(2,2)]
        while True:
            non_d = randint(0,3)
            r,c = options[non_d]
            if grid[r][c] == color:
                break
        return abs(r-2*flip),abs(c-2*abs(flip-1))

    # All subsequent rounds
    if turn > 3:
        # Play to win
        if [color,color,0] in grid:
            print "1"
            return grid.index([color,color,0]),2
        elif [color,color,0] in rotate_grid:
            print "2"
            return 2,rotate_grid.index([color,color,0])
        if [color,0,color] in grid:
            print "3"
            return grid.index([color,0,color]),1
        elif [color,0,color] in rotate_grid:
            print "4"
            return 1,rotate_grid.index([color,0,color])
        if [0,color,color] in grid:
            print "5"
            return grid.index([0,color,color]),0
        elif [0,color,color] in rotate_grid:
            print "6"
            return 0,rotate_grid.index([0,color,color])

        # Play to block
        if [op_color,op_color,0] in grid:
            print "7"
            return grid.index([op_color,op_color,0]),2
        elif[op_color,op_color,0] in rotate_grid:
           print "8" 
           return 2,rotate_grid.index([op_color,op_color,0])
        if [op_color,0,op_color] in grid:
            print "9"
            return grid.index([op_color,0,op_color]),1
        elif[op_color,0,op_color] in rotate_grid:
            print "10"
            return 1,rotate_grid.index([op_color,0,op_color])
        if [0,op_color,op_color] in grid:
            print "11"
            return grid.index([0,op_color,op_color]),0
        elif[0,op_color,op_color] in rotate_grid:
            print "12"
            return 0,rotate_grid.index([0,op_color,op_color])


    # Weird how turn 4 is addressed here, but it is an edge case
    if turn == 4 and \
       ((grid[0][0] == op_color and grid[2][2] == op_color) or \
        (grid[0][2] == op_color and grid[2][0] == op_color)):
        print "Symmetry catch"
        non_d = randint(0,3)
        options = [(0,1),(1,0),(1,2),(2,1)]
        return options[non_d]

    row = randint(0,2)
    column = randint(0,2)
    return row,column


def compute_win(grid):
    color = session['color']
    op_color = abs(session['color']-3)
    rotate_grid = [[grid[0][x],grid[1][x],grid[2][x]] \
                       for x,l in enumerate(grid)]


    if [color,color,color] in grid or [color,color,color] in rotate_grid:
        return color
    if [op_color,op_color,op_color] in grid \
       or [op_color,op_color,op_color] in rotate_grid:
        return op_color


    return 0



@app.route("/setup", methods=['GET'])
def setup():
    return render_template('setup.html');

@app.route("/setup", methods=['POST'])
def update_setup():
    session['grid'] = [[0,0,0],[0,0,0],[0,0,0]]
    session['color'] = parsenum(request.form['color'])
    session['order'] = parsenum(request.form['order'])
    session['turn'] = 0
    session['win'] = 0
    return redirect(url_for('index'))

@app.route("/restart")
def restart():
    session['grid'] = [[0,0,0],[0,0,0],[0,0,0]]
    session['turn'] = 0
    session['win'] = 0
    return redirect(url_for('index'))

@app.route("/", methods=['GET'])
def index():

    if not 'grid' in session:
        return redirect(url_for('setup'))

    # configure first time
    if session['order'] == 2 and session['turn'] == 0:
        session['turn'] += 1 
        while True:

            c_row,c_column = ttt_logic(session['grid'], 
                                       session['turn'], 
                                       abs(session['color']-3))

            if session['grid'][c_row][c_column] == 0:
                session['grid'][c_row][c_column] = abs(session['color']-3)
                break

    return render_template('index.html', 
                           grid=session['grid'],
                           turn = session['turn'],
                           win = session['win'])

@app.route("/", methods=['POST'])
def update():
    session['win'] = compute_win(session['grid']);
    if session['win'] == 0:
        # perform player move
        session['turn'] += 1
        p_row = parsenum(request.form['play'].split(',')[0])
        p_column = parsenum(request.form['play'].split(',')[1])
        if session['grid'][p_row][p_column] == 0:
            session['grid'][p_row][p_column] = session['color']
            
    
            # perform computer move
            session['turn'] += 1
            while True and session['turn'] < 10:
                
                c_row,c_column = ttt_logic(session['grid'], 
                                           session['turn'], 
                                           abs(session['color']-3))

                if session['grid'][c_row][c_column] == 0:
                    session['grid'][c_row][c_column] = abs(session['color']-3)
                    break

    session['win'] = compute_win(session['grid']);
    return render_template('index.html', 
                           grid=session['grid'],
                           turn = session['turn'],
                           win = session['win'])

if __name__ == "__main__":
    app.run(debug=True)
