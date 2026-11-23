var Ht=Object.defineProperty;var Nt=Object.getOwnPropertyDescriptor;var y=(r,t,e,s)=>{for(var i=s>1?void 0:s?Nt(t,e):t,n=r.length-1,o;n>=0;n--)(o=r[n])&&(i=(s?o(t,e,i):o(i))||i);return s&&i&&Ht(t,e,i),i};var I=globalThis,q=I.ShadowRoot&&(I.ShadyCSS===void 0||I.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,J=Symbol(),ht=new WeakMap,P=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==J)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(q&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=ht.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&ht.set(e,t))}return t}toString(){return this.cssText}},dt=r=>new P(typeof r=="string"?r:r+"",void 0,J),O=(r,...t)=>{let e=r.length===1?r[0]:t.reduce((s,i,n)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[n+1],r[0]);return new P(e,r,J)},pt=(r,t)=>{if(q)r.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=I.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,r.appendChild(s)}},X=q?r=>r:r=>r instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return dt(e)})(r):r;var{is:Mt,defineProperty:Ut,getOwnPropertyDescriptor:Dt,getOwnPropertyNames:Lt,getOwnPropertySymbols:kt,getPrototypeOf:jt}=Object,V=globalThis,ut=V.trustedTypes,zt=ut?ut.emptyScript:"",It=V.reactiveElementPolyfillSupport,H=(r,t)=>r,N={toAttribute(r,t){switch(t){case Boolean:r=r?zt:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,t){let e=r;switch(t){case Boolean:e=r!==null;break;case Number:e=r===null?null:Number(r);break;case Object:case Array:try{e=JSON.parse(r)}catch{e=null}}return e}},B=(r,t)=>!Mt(r,t),mt={attribute:!0,type:String,converter:N,reflect:!1,useDefault:!1,hasChanged:B};Symbol.metadata??=Symbol("metadata"),V.litPropertyMetadata??=new WeakMap;var g=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=mt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&Ut(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:n}=Dt(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:i,set(o){let l=i?.call(this);n?.call(this,o),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??mt}static _$Ei(){if(this.hasOwnProperty(H("elementProperties")))return;let t=jt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(H("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(H("properties"))){let e=this.properties,s=[...Lt(e),...kt(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(X(i))}else t!==void 0&&e.push(X(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return pt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let n=(s.converter?.toAttribute!==void 0?s.converter:N).toAttribute(e,s.type);this._$Em=t,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let n=s.getPropertyOptions(i),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:N;this._$Em=i;let l=o.fromAttribute(e,n.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(t,e,s,i=!1,n){if(t!==void 0){let o=this.constructor;if(i===!1&&(n=this[t]),s??=o.getPropertyOptions(t),!((s.hasChanged??B)(n,e)||s.useDefault&&s.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:n},o){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),n!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,n]of s){let{wrapped:o}=n,l=this[i];o!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,n,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};g.elementStyles=[],g.shadowRootOptions={mode:"open"},g[H("elementProperties")]=new Map,g[H("finalized")]=new Map,It?.({ReactiveElement:g}),(V.reactiveElementVersions??=[]).push("2.1.2");var nt=globalThis,ft=r=>r,W=nt.trustedTypes,gt=W?W.createPolicy("lit-html",{createHTML:r=>r}):void 0,bt="$lit$",$=`lit$${Math.random().toFixed(9).slice(2)}$`,wt="?"+$,qt=`<${wt}>`,w=document,U=()=>w.createComment(""),D=r=>r===null||typeof r!="object"&&typeof r!="function",ot=Array.isArray,Vt=r=>ot(r)||typeof r?.[Symbol.iterator]=="function",Q=`[ 	
\f\r]`,M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,_t=/-->/g,yt=/>/g,A=RegExp(`>|${Q}(?:([^\\s"'>=/]+)(${Q}*=${Q}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),$t=/'/g,vt=/"/g,Et=/^(?:script|style|textarea|title)$/i,at=r=>(t,...e)=>({_$litType$:r,strings:t,values:e}),u=at(1),re=at(2),ne=at(3),E=Symbol.for("lit-noChange"),c=Symbol.for("lit-nothing"),At=new WeakMap,b=w.createTreeWalker(w,129);function St(r,t){if(!ot(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return gt!==void 0?gt.createHTML(t):t}var Bt=(r,t)=>{let e=r.length-1,s=[],i,n=t===2?"<svg>":t===3?"<math>":"",o=M;for(let l=0;l<e;l++){let a=r[l],d,p,h=-1,f=0;for(;f<a.length&&(o.lastIndex=f,p=o.exec(a),p!==null);)f=o.lastIndex,o===M?p[1]==="!--"?o=_t:p[1]!==void 0?o=yt:p[2]!==void 0?(Et.test(p[2])&&(i=RegExp("</"+p[2],"g")),o=A):p[3]!==void 0&&(o=A):o===A?p[0]===">"?(o=i??M,h=-1):p[1]===void 0?h=-2:(h=o.lastIndex-p[2].length,d=p[1],o=p[3]===void 0?A:p[3]==='"'?vt:$t):o===vt||o===$t?o=A:o===_t||o===yt?o=M:(o=A,i=void 0);let _=o===A&&r[l+1].startsWith("/>")?" ":"";n+=o===M?a+qt:h>=0?(s.push(d),a.slice(0,h)+bt+a.slice(h)+$+_):a+$+(h===-2?l:_)}return[St(r,n+(r[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},L=class r{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let n=0,o=0,l=t.length-1,a=this.parts,[d,p]=Bt(t,e);if(this.el=r.createElement(d,s),b.currentNode=this.el.content,e===2||e===3){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(i=b.nextNode())!==null&&a.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(let h of i.getAttributeNames())if(h.endsWith(bt)){let f=p[o++],_=i.getAttribute(h).split($),z=/([.?@])?(.*)/.exec(f);a.push({type:1,index:n,name:z[2],strings:_,ctor:z[1]==="."?et:z[1]==="?"?st:z[1]==="@"?it:R}),i.removeAttribute(h)}else h.startsWith($)&&(a.push({type:6,index:n}),i.removeAttribute(h));if(Et.test(i.tagName)){let h=i.textContent.split($),f=h.length-1;if(f>0){i.textContent=W?W.emptyScript:"";for(let _=0;_<f;_++)i.append(h[_],U()),b.nextNode(),a.push({type:2,index:++n});i.append(h[f],U())}}}else if(i.nodeType===8)if(i.data===wt)a.push({type:2,index:n});else{let h=-1;for(;(h=i.data.indexOf($,h+1))!==-1;)a.push({type:7,index:n}),h+=$.length-1}n++}}static createElement(t,e){let s=w.createElement("template");return s.innerHTML=t,s}};function C(r,t,e=r,s){if(t===E)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,n=D(t)?void 0:t._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(r),i._$AT(r,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=C(r,i._$AS(r,t.values),i,s)),t}var tt=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??w).importNode(e,!0);b.currentNode=i;let n=b.nextNode(),o=0,l=0,a=s[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new k(n,n.nextSibling,this,t):a.type===1?d=new a.ctor(n,a.name,a.strings,this,t):a.type===6&&(d=new rt(n,this,t)),this._$AV.push(d),a=s[++l]}o!==a?.index&&(n=b.nextNode(),o++)}return b.currentNode=w,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},k=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=c,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=C(this,t,e),D(t)?t===c||t==null||t===""?(this._$AH!==c&&this._$AR(),this._$AH=c):t!==this._$AH&&t!==E&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Vt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==c&&D(this._$AH)?this._$AA.nextSibling.data=t:this.T(w.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=L.createElement(St(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let n=new tt(i,this),o=n.u(this.options);n.p(e),this.T(o),this._$AH=n}}_$AC(t){let e=At.get(t.strings);return e===void 0&&At.set(t.strings,e=new L(t)),e}k(t){ot(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let n of t)i===e.length?e.push(s=new r(this.O(U()),this.O(U()),this,this.options)):s=e[i],s._$AI(n),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=ft(t).nextSibling;ft(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},R=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,n){this.type=1,this._$AH=c,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=c}_$AI(t,e=this,s,i){let n=this.strings,o=!1;if(n===void 0)t=C(this,t,e,0),o=!D(t)||t!==this._$AH&&t!==E,o&&(this._$AH=t);else{let l=t,a,d;for(t=n[0],a=0;a<n.length-1;a++)d=C(this,l[s+a],e,a),d===E&&(d=this._$AH[a]),o||=!D(d)||d!==this._$AH[a],d===c?t=c:t!==c&&(t+=(d??"")+n[a+1]),this._$AH[a]=d}o&&!i&&this.j(t)}j(t){t===c?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},et=class extends R{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===c?void 0:t}},st=class extends R{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==c)}},it=class extends R{constructor(t,e,s,i,n){super(t,e,s,i,n),this.type=5}_$AI(t,e=this){if((t=C(this,t,e,0)??c)===E)return;let s=this._$AH,i=t===c&&s!==c||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,n=t!==c&&(s===c||i);i&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},rt=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){C(this,t)}};var Wt=nt.litHtmlPolyfillSupport;Wt?.(L,k),(nt.litHtmlVersions??=[]).push("3.3.3");var xt=(r,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let n=e?.renderBefore??null;s._$litPart$=i=new k(t.insertBefore(U(),n),n,void 0,e??{})}return i._$AI(r),i};var lt=globalThis,m=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=xt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return E}};m._$litElement$=!0,m.finalized=!0,lt.litElementHydrateSupport?.({LitElement:m});var Ft=lt.litElementPolyfillSupport;Ft?.({LitElement:m});(lt.litElementVersions??=[]).push("4.2.2");var F=r=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(r,t)}):customElements.define(r,t)};var Yt={attribute:!0,type:String,converter:N,reflect:!1,hasChanged:B},Kt=(r=Yt,t,e)=>{let{kind:s,metadata:i}=e,n=globalThis.litPropertyMetadata.get(i);if(n===void 0&&globalThis.litPropertyMetadata.set(i,n=new Map),s==="setter"&&((r=Object.create(r)).wrapped=!0),n.set(e.name,r),s==="accessor"){let{name:o}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(o,a,r,!0,l)},init(l){return l!==void 0&&this.C(o,void 0,r,l),l}}}if(s==="setter"){let{name:o}=e;return function(l){let a=this[o];t.call(this,l),this.requestUpdate(o,a,r,!0,l)}}throw Error("Unsupported decorator location: "+s)};function T(r){return(t,e)=>typeof e=="object"?Kt(r,t,e):((s,i,n)=>{let o=i.hasOwnProperty(n);return i.constructor.createProperty(n,s),o?Object.getOwnPropertyDescriptor(i,n):void 0})(r,t,e)}function Y(r){return T({...r,state:!0,attribute:!1})}var Ct="1.1.0";var G="meteoalarm-card",Z="meteoalarm-card-editor",j={none:"var(--success-color, #4caf50)",minor:"var(--info-color, #43a047)",moderate:"var(--warning-color, #ffb300)",severe:"var(--meteoalarm-severe-color, #ff7043)",extreme:"var(--error-color, #f44336)"},Gt=[["wind","mdi:weather-windy"],["snow","mdi:snowflake-alert"],["ice","mdi:snowflake-alert"],["thunder","mdi:weather-lightning-rainy"],["fog","mdi:weather-fog"],["high-temp","mdi:thermometer-plus"],["high temp","mdi:thermometer-plus"],["heat","mdi:thermometer-plus"],["low-temp","mdi:thermometer-minus"],["low temp","mdi:thermometer-minus"],["cold","mdi:thermometer-minus"],["coastal","mdi:waves-arrow-up"],["fire","mdi:pine-tree-fire"],["avalanche","mdi:landslide"],["rain-flood","mdi:home-flood"],["flood","mdi:home-flood"],["rain","mdi:weather-pouring"]];function Rt(r,t){let e=`${r??""} ${t??""}`.toLowerCase();for(let[s,i]of Gt)if(e.includes(s))return i;return"mdi:alert-outline"}var Tt={en:{no_warnings:"No active warnings",until:"until",show_details:"Show details",entity_missing:"Entity not found:",entity_required:"Please set an entity of the MeteoAlarm integration",entity_unavailable:"Warnings are currently unavailable",entity_wrong:"This entity has no warnings. Select the warning level sensor."},lv:{no_warnings:"Nav akt\u012Bvu br\u012Bdin\u0101jumu",until:"l\u012Bdz",show_details:"R\u0101d\u012Bt deta\u013Cas",entity_missing:"Vien\u012Bba nav atrasta:",entity_required:"Nor\u0101di MeteoAlarm integr\u0101cijas vien\u012Bbu",entity_unavailable:"Br\u012Bdin\u0101jumi pa\u0161laik nav pieejami",entity_wrong:"\u0160ai vien\u012Bbai nav br\u012Bdin\u0101jumu. Izv\u0113lies br\u012Bdin\u0101juma l\u012Bme\u0146a sensoru."}};function ct(r){return(r?.locale?.language??r?.language??"en").split("-")[0]}function v(r,t){let e=ct(r);return Tt[e]?.[t]??Tt.en[t]??t}var Zt=[{name:"entity",required:!0,selector:{entity:{filter:[{integration:"meteoalarm_custom",domain:"sensor",device_class:"enum"}]}}},{name:"title",selector:{text:{}}},{name:"show_description",default:!0,selector:{boolean:{}}},{name:"show_instruction",selector:{boolean:{}}},{name:"compact",selector:{boolean:{}}}],Pt={en:{entity:"Entity (warning level sensor)",title:"Title",show_description:"Show warning description",show_instruction:"Show instructions",compact:"Compact mode"},lv:{entity:"Vien\u012Bba (br\u012Bdin\u0101juma l\u012Bme\u0146a sensors)",title:"Virsraksts",show_description:"R\u0101d\u012Bt br\u012Bdin\u0101juma aprakstu",show_instruction:"R\u0101d\u012Bt nor\u0101d\u012Bjumus",compact:"Kompaktais re\u017E\u012Bms"}},S=class extends m{constructor(){super(...arguments);this._computeLabel=e=>{let s=ct(this.hass);return Pt[s]?.[e.name]??Pt.en[e.name]??e.name}}setConfig(e){this._config=e}_valueChanged(e){e.stopPropagation();let s=e.detail.value;this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:s},bubbles:!0,composed:!0}))}render(){return!this.hass||!this._config?c:u`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${Zt}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}};S.styles=O`
    ha-form {
      display: block;
    }
  `,y([T({attribute:!1})],S.prototype,"hass",2),y([Y()],S.prototype,"_config",2),S=y([F(Z)],S);function Jt(r){return r?.locale?.time_zone==="server"?r.config?.time_zone:void 0}function Ot(r,t,e=new Date){if(!r)return"";let s=new Date(r);if(Number.isNaN(s.getTime()))return"";let i=t?.locale?.language??t?.language??"en",n=Jt(t),o=t?.locale?.time_format,l=d=>new Intl.DateTimeFormat("en-CA",{timeZone:n,year:"numeric",month:"2-digit",day:"2-digit"}).format(d),a=l(e)===l(s);return new Intl.DateTimeFormat(i,{timeZone:n,hour12:o==="12"?!0:void 0,hourCycle:o==="24"?"h23":void 0,...a?{}:{day:"numeric",month:"short"},hour:"2-digit",minute:"2-digit"}).format(s)}console.info(`%c METEOALARM-CARD %c ${Ct} `,"color: white; background: #e65100; font-weight: 700;","color: #e65100; background: white; font-weight: 700;");window.customCards=window.customCards??[];window.customCards.some(r=>r.type===G)||window.customCards.push({type:G,name:"MeteoAlarm Card",description:"Shows active MeteoAlarm weather warnings for a region.",preview:!0,documentationURL:"https://github.com/gatisr/meteoalarm_custom"});var x=class extends m{static async getConfigElement(){return document.createElement(Z)}static getStubConfig(t){return{entity:Object.values(t.states).find(s=>s.entity_id.startsWith("sensor.")&&s.attributes.device_class==="enum"&&Array.isArray(s.attributes.alerts))?.entity_id}}getGridOptions(){return{columns:12,min_columns:6,rows:"auto"}}setConfig(t){this._config={show_description:!0,...t}}getCardSize(){return 1+(this._entity()?.attributes.alerts?.length??0)*2}shouldUpdate(t){if(t.has("_config"))return!0;let e=t.get("hass");return!e||!this._config?.entity?!0:e.states[this._config.entity]!==this.hass?.states[this._config.entity]}_entity(){if(!(!this.hass||!this._config?.entity))return this.hass.states[this._config.entity]}_title(t){if(this._config?.title)return this._config.title;let e=t?.attributes.area;return e||(t?.attributes.friendly_name??"MeteoAlarm")}_formatTime(t){return Ot(t,this.hass)}_timeRange(t){let e=this._formatTime(t.onset),s=this._formatTime(t.expires);return e&&s?`${e} \u2013 ${s}`:s?`${v(this.hass,"until")} ${s}`:e}render(){if(!this._config)return c;if(!this._config.entity)return this._warning(v(this.hass,"entity_required"));let t=this._entity();if(!t)return this._warning(`${v(this.hass,"entity_missing")} ${this._config.entity}`);if(t.state==="unavailable"||t.state==="unknown")return this._warning(v(this.hass,"entity_unavailable"));if(!Array.isArray(t.attributes.alerts))return this._warning(v(this.hass,"entity_wrong"));let e=t.attributes.alerts,s=Object.hasOwn(j,t.state)?t.state:"none",i=j[s],n=this.hass?.formatEntityState?.(t)??t.state;return u`
      <ha-card>
        <div class="header">
          <ha-icon class="header-icon" style="color: ${i}"
            icon=${e.length?"mdi:alert-decagram":"mdi:shield-check"}
          ></ha-icon>
          <div class="name">${this._title(t)}</div>
          <div class="badge ${s}" style="background: ${i}">${n}</div>
        </div>
        ${e.length===0?u`<div class="calm">${v(this.hass,"no_warnings")}</div>`:e.map(o=>this._renderAlert(o))}
      </ha-card>
    `}_renderAlert(t){let e=j[t.severity]??j.none,s=this._config?.compact??!1;return u`
      <div class="alert" style="border-color: ${e}">
        <ha-icon aria-hidden="true" icon=${Rt(t.awareness_type,t.event)} style="color: ${e}"></ha-icon>
        <div class="alert-body">
          <div class="event">${t.event??t.headline??""}</div>
          <div class="time">${this._timeRange(t)}</div>
          ${s?c:this._renderTexts(t)}
        </div>
      </div>
    `}_renderTexts(t){let e=this._config?.show_description?t.description:null,s=this._config?.show_instruction?t.instruction:null,i=(e?.length??0)>200;return u`
      ${e?i?u`<details>
              <summary>${v(this.hass,"show_details")}</summary>
              <div class="description">${e}</div>
            </details>`:u`<div class="description">${e}</div>`:c}
      ${s?u`<div class="instruction">${s}</div>`:c}
    `}_warning(t){return u`<ha-card><div class="calm">${t}</div></ha-card>`}};x.styles=O`
    ha-card {
      padding: 12px 16px 16px;
    }
    .header {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 4px 0 8px;
    }
    .header-icon {
      --mdc-icon-size: 26px;
    }
    .name {
      flex: 1;
      font-size: 1.15rem;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .badge {
      flex-shrink: 0;
      white-space: nowrap;
      color: #fff;
      border-radius: 12px;
      padding: 3px 10px;
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    /* White text is unreadable on the yellow. */
    .badge.moderate {
      color: #000;
    }
    .calm {
      color: var(--secondary-text-color);
      padding: 4px 0;
    }
    .alert {
      display: flex;
      gap: 12px;
      align-items: flex-start;
      border-left: 4px solid;
      border-radius: 4px;
      background: var(--secondary-background-color, rgba(0, 0, 0, 0.04));
      padding: 10px 12px;
      margin-top: 8px;
    }
    .alert ha-icon {
      --mdc-icon-size: 24px;
      margin-top: 2px;
    }
    .alert-body {
      flex: 1;
      min-width: 0;
    }
    .event {
      overflow-wrap: anywhere;
      font-weight: 500;
    }
    .time {
      color: var(--secondary-text-color);
      font-size: 0.85rem;
      margin-top: 2px;
    }
    .description,
    .instruction {
      font-size: 0.9rem;
      margin-top: 6px;
      white-space: pre-line;
      overflow-wrap: anywhere;
    }
    .instruction {
      color: var(--secondary-text-color);
      font-style: italic;
    }
    summary {
      cursor: pointer;
      color: var(--primary-color);
      font-size: 0.85rem;
      margin-top: 6px;
    }
  `,y([T({attribute:!1})],x.prototype,"hass",2),y([Y()],x.prototype,"_config",2),x=y([F(G)],x);export{x as MeteoAlarmCard};
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
@lit/reactive-element/decorators/custom-element.js:
@lit/reactive-element/decorators/property.js:
@lit/reactive-element/decorators/state.js:
@lit/reactive-element/decorators/event-options.js:
@lit/reactive-element/decorators/base.js:
@lit/reactive-element/decorators/query.js:
@lit/reactive-element/decorators/query-all.js:
@lit/reactive-element/decorators/query-async.js:
@lit/reactive-element/decorators/query-assigned-nodes.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
