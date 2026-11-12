import {useState} from 'react';
import './cell.css';

function Cell({value, onCellClick}) {

    return (
        <button className = "cell" onClick = {onCellClick}>
            {value}
        </button>
    )
}

export function Board({dim}: {dim: number}) {
    const [gameState,setState] = useState(Array(dim*dim).fill(null));
    const [turn,setTurn] = useState("Black")

    function nextTurn() {
        if (turn == "White") {
            setTurn("Black");
        } 
        else {
            setTurn("White");
        }
    }

    function getAdj(i) {
        /*Get cells adjacent to cell i*/
        return [i-dim,i-1,i+1,i+dim];
    }

    function getGroup(i) {
        /*Return orthogonally adjacent group to i */
        let stateCopy = gameState.slice();
        let color = stateCopy[i];
        let group = new Set([]);
        let adj = [0,0,0];
        let visits = [i];
        while (visits.length > 0) {
            let temp = visits.shift();
            if (!group.has(temp)) {
                group.add(temp);
                for (const a of getAdj(temp)) {
                    if (a >= 0 && a < (dim*dim)) {
                        if (stateCopy[a] == color) {
                            visits.push(a);
                        }
                        if (stateCopy[a] == null) {
                            adj[0] = adj[0] + 1;
                        }
                        else if (stateCopy[a] == "X") {
                            adj[1] = adj[1] + 1;
                        }
                        else {
                            adj[2] = adj[2] + 1;
                        }
                    }
                }
            }
        }
        return [group,adj];
    }

    function quickSet(i,value) {
        let nextCell = gameState.slice();
        if (turn == "White") {
            nextCell[i] = value;
        }
        else {
            nextCell[i] = value;
        }
        setState(nextCell);
    }

    function onClick(i) {
        console.log("Turn is",turn);
        let currentcolor = (turn === "White" ? "O": "X");
        let oppcolor = (turn === "White" ? "X": "O");
        /*Check if current move will capture */
        console.log(gameState);

        //console.log("Clicked");
        if (legalMove(i)) {
            console.log("Move is legal");
            const captureCell = gameState.slice();
            captureCell[i] = currentcolor;
            for (const a of getAdj(i)) {
                if (captureCell[a] == oppcolor) {
                    let agroup = getGroup(a);
                    if (agroup[1][0] == 0) {
                        for (const b of agroup[0]) {
                            captureCell[b].value = null;
                        }
                    }
                }
            }
            console.log("Captures executed");
            nextTurn();
            setState(captureCell);
            return true;
        }
        else {
            console.log("Move illegal");
            let revertCell = gameState.slice();
            revertCell[i] = null;
            return false;
        }
    }

    function legalMove(i) {
        /*Go move is legal if: square is empty, doesn't result in group with no liberties unless capturing */
        /*Skipping Ko rule for now */
        console.log("Entered legal move");
        let currentcolor = (turn === "White" ? "O" : "X");
        let opcolor = (turn === "White" ? "X" : "O");
        if (gameState[i] != null) {
            return false;
        }
        let willCapture = false;
        for (const a of getAdj(i)) {
            console.log("Examining square",a);
            if (gameState[a] == opcolor) {
                let agroup = getGroup(a);
                if (agroup[1][0] == 1) {
                    willCapture = true;
                }
            }
        }
        let sgroup = getGroup(i);
        if (sgroup[1][0] == 0 && !willCapture) {
            return false;
        }
        return true;
    }

    return (
        <div>
            {Array.from({length:dim},(_,indexy) => (
                <div className = "board-row">
                    {Array.from({length:dim},(_,indexx) => (
                        <Cell value = {gameState[indexx + (indexy * dim)]} onCellClick = {() => onClick(indexx + (indexy * dim))} />
                    ))}
                </div>
            ))}
        </div>
    )
}