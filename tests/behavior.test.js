import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Behavior,clampPosition} from '../src/core/behavior.js';
test('long wake delta is bounded, paused time cannot accumulate',()=>{const b=new Behavior(); b.tick(3600); assert.equal(b.time,0.1); b.setPaused(true); b.tick(1); assert.equal(b.time,0.1);});
test('pet feedback obeys cooldown and pause',()=>{const b=new Behavior(); assert.equal(b.pet(),true); assert.equal(b.pet(),false); for(let i=0;i<20;i++) b.tick(.1); assert.equal(b.pet(),true); b.setPaused(true); assert.equal(b.pet(),false);});
test('sleep wakes via stretch and reduced motion excludes walking',()=>{const b=new Behavior(()=>0); b.choose('sleep',.1); b.tick(.1); assert.equal(b.state,'stretch'); b.choose('walk',3); b.setReduced(true); assert.equal(b.state,'idle'); for(let i=0;i<1000;i++){b.tick(.1); assert.notEqual(b.state,'walk');}});
test('unknown intents cannot execute and invalid delta is ignored',()=>{const b=new Behavior(); assert.equal(b.choose('execute-shell',1),false); b.tick(NaN); assert.equal(b.time,0);});
test('placement handles negative monitors and undersized work areas',()=>{assert.deepEqual(clampPosition(-3000,900,{x:-1920,y:0,width:1920,height:1080},300,260),{x:-1920,y:820}); assert.deepEqual(clampPosition(900,900,{x:0,y:0,width:100,height:100},300,260),{x:0,y:0});});
