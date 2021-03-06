import fs from 'fs';
import { exit } from 'process';

let rows = fs.readFileSync("src/Untitled.csv", 'ascii').split("\n");
let irow = 0;

const mem = [];

function dump(){
    return irow+1 + " "+  rows[irow];
}

function acceptDisable(){
    if (rows[irow].split(',')[1] == '"disable"'){
        irow++;
        return true;
    } else {
        return false;
    }
}

function acceptEnable(){
    if (rows[irow].split(',')[1] == '"enable"'){
        irow++;
        return true;
    } else {
        return false;
    }
}

function expectEnable(){
   if(!acceptEnable()){ throw new Error(dump() + 'expected "enable"')}
}

function expectDisable(){
    if(!acceptDisable()){ throw new Error(dump() + 'expected "disable"')}
 }
function arg1(){
    return parseInt(rows[irow++].split(',')[3]);
}

function arg2(){
    return parseInt(rows[irow++].split(',')[4]);
}

function acceptOp(op: string){
    if (rows[irow].split(',')[3] == op){
        irow++;
        return true;
    } else {
        return false;
    }
}
function read(){
    if (acceptOp('0x03')) {
        console.log('read');
        let addr = arg1() * 65536 + arg1() * 256 + arg1();
        while(!acceptDisable()){
            mem[addr++] = arg2();
        }
        return true;
    } 
    return false;
}


function writeEnable(){
    if (acceptOp('0x06')) {
        console.log('writeEnable');
        expectDisable();
        expectEnable();
        return true;
    } 
    return false;
}


function writeDisable(){
    if (acceptOp('0x04')) {
        console.log('writeDisable');
        expectDisable();
        expectEnable();
        return true;
    } 
    return false;
}

function readStatus(){
    if (acceptOp('0x05')) {
        console.log('readStatus');
        arg1();
        expectDisable();
        expectEnable();
        return true;
    } 
    return false;
}

function toProgramOneDataByte(){
    if (acceptOp('0x02')) {
        console.log('To Program One Data Byte');
        let waddr = arg1() * 65536 + arg1() * 256 + arg1();
        mem[waddr] = arg1();
        expectDisable();
        expectEnable();
        return true;
    }
    return false;   
}
function aaid(){

    if (acceptOp('0xAD')) {
        console.log('Auto Address Increment Programming');
        let waddr = arg1() * 65536 + arg1() * 256 + arg1();
     

        while(true){
            mem[waddr++] = arg1();
            mem[waddr++] = arg1();
            expectDisable();
            expectEnable();
            if(!acceptOp('0x05')){
                break;
            }

            arg2();
            expectDisable();
            expectEnable();

            if (!acceptOp('0xAD')){
                break;
            }
        }
        return true;
    } 
    return false;
}


while(irow < rows.length){
    acceptEnable();
    if(read() || writeEnable() || aaid() ||
        writeDisable() || readStatus() || toProgramOneDataByte()){
       ; 
    }
    else {
        console.log(irow+1,  rows[irow]);
        exit(0);
    }
}


const b = new Uint8Array(mem);
fs.writeFileSync('result.x', b);
console.log(b.length);