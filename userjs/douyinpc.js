// ==UserScript==
// @name         抖音PC快捷键
// @namespace    http://tampermonkey.net/
// @version      0.1
// @author       wx c
// @match        https://www.douyin.com/recommend*
// @icon         https://lf1-cdn-tos.bytegoofy.com/goofy/ies/douyin_web/public/favicon.ico
// @grant        none
// ==/UserScript==
//https://github.com/sahithyandev/KeyboardMaster
var KeyboardMaster=(()=>{var g=(t,e)=>()=>(e||(e={exports:{}},t(e.exports,e)),e.exports),f=g((u,p)=>{HTMLElement.prototype.addKeyBindings=function(t){this.pressed=new Set,this.keyBindings=t,t.seperator=t.seperator!=null?t.seperator:" + ",this.checkKeyBinding=function(){const e=Array.from(this.pressed);this.keyBindings.bindings.forEach(i=>{e.join(t.seperator).toLowerCase()===d(i.keyBinding,t.seperator).toLowerCase()&&i.action.call(this,i.keyBinding)})},this.onkeyup=e=>{this.pressed.delete(s(e.key)),o("deleting key from storage",this.pressed)},this.onkeydown=e=>{this.pressed.add(s(e.key)),this.checkKeyBinding(e),o(e.key),o("adding key to storage",this.pressed)},o(`bindings added for ${this}`)};HTMLElement.prototype.removeAllKeyBindings=function(){o(this),this.keyBindings.bindings=[]};p.exports={updateConfig:a}});const r={mode:"development"};function a(t){for(const e in t)r[e]=t[e];o("config update to",r)}const o=(...t)=>{r.mode==="development"&&console.log(...t)};function d(t,e){return t.split(e).map(i=>{let n=i;return i.toLowerCase()=="ctrl"&&(n="Control"),i.toLowerCase()=="shift"&&(n="Shift"),n}).join(e)}function s(t){let e=t;const i={" ":"Space"};return i[t]&&(e=i[t]),e}return f();})();
(function() {
    'use strict';
    /**
    ctrl  + enter 点赞
    shift + enter 打开评论区
    alt   + enter 关注/取关
    */
    document.body.addKeyBindings({
        seperator: ' + ', // If undefined, defaults to this value
        bindings: [
            {
                keyBinding: 'ctrl + enter',
                action: () => {
                    document.querySelector('div.xgplayer-video-interaction-wrap > div > div:nth-child(2)').click();
                }
            },
            {
                keyBinding: 'shift + enter',
                action: () => {
                    document.querySelector('div.xgplayer-video-interaction-wrap > div > div:nth-child(3)').click();
                }
            },
            {
                keyBinding: 'alt + enter',
                action: () => {
                    document.querySelector('div.xgplayer-video-interaction-wrap > div > div:nth-child(1)').click();
                }
            },
        ]
    });

    // Your code here...
})();