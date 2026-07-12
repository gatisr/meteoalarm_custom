var Tt=Object.defineProperty;var Ot=Object.getOwnPropertyDescriptor;var $=(r,t,e,s)=>{for(var i=s>1?void 0:s?Ot(t,e):t,n=r.length-1,o;n>=0;n--)(o=r[n])&&(i=(s?o(t,e,i):o(i))||i);return s&&i&&Tt(t,e,i),i};var z=globalThis,I=z.ShadowRoot&&(z.ShadyCSS===void 0||z.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),lt=new WeakMap,R=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(I&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=lt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&lt.set(e,t))}return t}toString(){return this.cssText}},ht=r=>new R(typeof r=="string"?r:r+"",void 0,Z),T=(r,...t)=>{let e=r.length===1?r[0]:t.reduce((s,i,n)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[n+1],r[0]);return new R(e,r,Z)},dt=(r,t)=>{if(I)r.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=z.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,r.appendChild(s)}},G=I?r=>r:r=>r instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return ht(e)})(r):r;var{is:Ht,defineProperty:Mt,getOwnPropertyDescriptor:Nt,getOwnPropertyNames:Ut,getOwnPropertySymbols:Dt,getPrototypeOf:Lt}=Object,V=globalThis,pt=V.trustedTypes,kt=pt?pt.emptyScript:"",jt=V.reactiveElementPolyfillSupport,O=(r,t)=>r,H={toAttribute(r,t){switch(t){case Boolean:r=r?kt:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,t){let e=r;switch(t){case Boolean:e=r!==null;break;case Number:e=r===null?null:Number(r);break;case Object:case Array:try{e=JSON.parse(r)}catch{e=null}}return e}},B=(r,t)=>!Ht(r,t),ut={attribute:!0,type:String,converter:H,reflect:!1,useDefault:!1,hasChanged:B};Symbol.metadata??=Symbol("metadata"),V.litPropertyMetadata??=new WeakMap;var f=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ut){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&Mt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:n}=Nt(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:i,set(o){let c=i?.call(this);n?.call(this,o),this.requestUpdate(t,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ut}static _$Ei(){if(this.hasOwnProperty(O("elementProperties")))return;let t=Lt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(O("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(O("properties"))){let e=this.properties,s=[...Ut(e),...Dt(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(G(i))}else t!==void 0&&e.push(G(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return dt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let n=(s.converter?.toAttribute!==void 0?s.converter:H).toAttribute(e,s.type);this._$Em=t,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let n=s.getPropertyOptions(i),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:H;this._$Em=i;let c=o.fromAttribute(e,n.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(t,e,s,i=!1,n){if(t!==void 0){let o=this.constructor;if(i===!1&&(n=this[t]),s??=o.getPropertyOptions(t),!((s.hasChanged??B)(n,e)||s.useDefault&&s.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:n},o){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),n!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,n]of s){let{wrapped:o}=n,c=this[i];o!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,n,c)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};f.elementStyles=[],f.shadowRootOptions={mode:"open"},f[O("elementProperties")]=new Map,f[O("finalized")]=new Map,jt?.({ReactiveElement:f}),(V.reactiveElementVersions??=[]).push("2.1.2");var rt=globalThis,mt=r=>r,W=rt.trustedTypes,ft=W?W.createPolicy("lit-html",{createHTML:r=>r}):void 0,At="$lit$",y=`lit$${Math.random().toFixed(9).slice(2)}$`,bt="?"+y,qt=`<${bt}>`,b=document,N=()=>b.createComment(""),U=r=>r===null||typeof r!="object"&&typeof r!="function",nt=Array.isArray,zt=r=>nt(r)||typeof r?.[Symbol.iterator]=="function",Q=`[ 	
\f\r]`,M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,gt=/-->/g,_t=/>/g,v=RegExp(`>|${Q}(?:([^\\s"'>=/]+)(${Q}*=${Q}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),$t=/'/g,yt=/"/g,wt=/^(?:script|style|textarea|title)$/i,ot=r=>(t,...e)=>({_$litType$:r,strings:t,values:e}),g=ot(1),te=ot(2),ee=ot(3),w=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),vt=new WeakMap,A=b.createTreeWalker(b,129);function Et(r,t){if(!nt(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return ft!==void 0?ft.createHTML(t):t}var It=(r,t)=>{let e=r.length-1,s=[],i,n=t===2?"<svg>":t===3?"<math>":"",o=M;for(let c=0;c<e;c++){let a=r[c],d,p,l=-1,m=0;for(;m<a.length&&(o.lastIndex=m,p=o.exec(a),p!==null);)m=o.lastIndex,o===M?p[1]==="!--"?o=gt:p[1]!==void 0?o=_t:p[2]!==void 0?(wt.test(p[2])&&(i=RegExp("</"+p[2],"g")),o=v):p[3]!==void 0&&(o=v):o===v?p[0]===">"?(o=i??M,l=-1):p[1]===void 0?l=-2:(l=o.lastIndex-p[2].length,d=p[1],o=p[3]===void 0?v:p[3]==='"'?yt:$t):o===yt||o===$t?o=v:o===gt||o===_t?o=M:(o=v,i=void 0);let _=o===v&&r[c+1].startsWith("/>")?" ":"";n+=o===M?a+qt:l>=0?(s.push(d),a.slice(0,l)+At+a.slice(l)+y+_):a+y+(l===-2?c:_)}return[Et(r,n+(r[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},D=class r{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let n=0,o=0,c=t.length-1,a=this.parts,[d,p]=It(t,e);if(this.el=r.createElement(d,s),A.currentNode=this.el.content,e===2||e===3){let l=this.el.content.firstChild;l.replaceWith(...l.childNodes)}for(;(i=A.nextNode())!==null&&a.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let l of i.getAttributeNames())if(l.endsWith(At)){let m=p[o++],_=i.getAttribute(l).split(y),q=/([.?@])?(.*)/.exec(m);a.push({type:1,index:n,name:q[2],strings:_,ctor:q[1]==="."?tt:q[1]==="?"?et:q[1]==="@"?st:C}),i.removeAttribute(l)}else l.startsWith(y)&&(a.push({type:6,index:n}),i.removeAttribute(l));if(wt.test(i.tagName)){let l=i.textContent.split(y),m=l.length-1;if(m>0){i.textContent=W?W.emptyScript:"";for(let _=0;_<m;_++)i.append(l[_],N()),A.nextNode(),a.push({type:2,index:++n});i.append(l[m],N())}}}else if(i.nodeType===8)if(i.data===bt)a.push({type:2,index:n});else{let l=-1;for(;(l=i.data.indexOf(y,l+1))!==-1;)a.push({type:7,index:n}),l+=y.length-1}n++}}static createElement(t,e){let s=b.createElement("template");return s.innerHTML=t,s}};function x(r,t,e=r,s){if(t===w)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,n=U(t)?void 0:t._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(r),i._$AT(r,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=x(r,i._$AS(r,t.values),i,s)),t}var X=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??b).importNode(e,!0);A.currentNode=i;let n=A.nextNode(),o=0,c=0,a=s[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new L(n,n.nextSibling,this,t):a.type===1?d=new a.ctor(n,a.name,a.strings,this,t):a.type===6&&(d=new it(n,this,t)),this._$AV.push(d),a=s[++c]}o!==a?.index&&(n=A.nextNode(),o++)}return A.currentNode=b,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},L=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=x(this,t,e),U(t)?t===h||t==null||t===""?(this._$AH!==h&&this._$AR(),this._$AH=h):t!==this._$AH&&t!==w&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):zt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==h&&U(this._$AH)?this._$AA.nextSibling.data=t:this.T(b.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=D.createElement(Et(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let n=new X(i,this),o=n.u(this.options);n.p(e),this.T(o),this._$AH=n}}_$AC(t){let e=vt.get(t.strings);return e===void 0&&vt.set(t.strings,e=new D(t)),e}k(t){nt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let n of t)i===e.length?e.push(s=new r(this.O(N()),this.O(N()),this,this.options)):s=e[i],s._$AI(n),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=mt(t).nextSibling;mt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},C=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,n){this.type=1,this._$AH=h,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=h}_$AI(t,e=this,s,i){let n=this.strings,o=!1;if(n===void 0)t=x(this,t,e,0),o=!U(t)||t!==this._$AH&&t!==w,o&&(this._$AH=t);else{let c=t,a,d;for(t=n[0],a=0;a<n.length-1;a++)d=x(this,c[s+a],e,a),d===w&&(d=this._$AH[a]),o||=!U(d)||d!==this._$AH[a],d===h?t=h:t!==h&&(t+=(d??"")+n[a+1]),this._$AH[a]=d}o&&!i&&this.j(t)}j(t){t===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},tt=class extends C{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===h?void 0:t}},et=class extends C{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==h)}},st=class extends C{constructor(t,e,s,i,n){super(t,e,s,i,n),this.type=5}_$AI(t,e=this){if((t=x(this,t,e,0)??h)===w)return;let s=this._$AH,i=t===h&&s!==h||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,n=t!==h&&(s===h||i);i&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},it=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){x(this,t)}};var Vt=rt.litHtmlPolyfillSupport;Vt?.(D,L),(rt.litHtmlVersions??=[]).push("3.3.3");var St=(r,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let n=e?.renderBefore??null;s._$litPart$=i=new L(t.insertBefore(N(),n),n,void 0,e??{})}return i._$AI(r),i};var at=globalThis,u=class extends f{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=St(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}};u._$litElement$=!0,u.finalized=!0,at.litElementHydrateSupport?.({LitElement:u});var Bt=at.litElementPolyfillSupport;Bt?.({LitElement:u});(at.litElementVersions??=[]).push("4.2.2");var Y=r=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(r,t)}):customElements.define(r,t)};var Wt={attribute:!0,type:String,converter:H,reflect:!1,hasChanged:B},Yt=(r=Wt,t,e)=>{let{kind:s,metadata:i}=e,n=globalThis.litPropertyMetadata.get(i);if(n===void 0&&globalThis.litPropertyMetadata.set(i,n=new Map),s==="setter"&&((r=Object.create(r)).wrapped=!0),n.set(e.name,r),s==="accessor"){let{name:o}=e;return{set(c){let a=t.get.call(this);t.set.call(this,c),this.requestUpdate(o,a,r,!0,c)},init(c){return c!==void 0&&this.C(o,void 0,r,c),c}}}if(s==="setter"){let{name:o}=e;return function(c){let a=this[o];t.call(this,c),this.requestUpdate(o,a,r,!0,c)}}throw Error("Unsupported decorator location: "+s)};function P(r){return(t,e)=>typeof e=="object"?Yt(r,t,e):((s,i,n)=>{let o=i.hasOwnProperty(n);return i.constructor.createProperty(n,s),o?Object.getOwnPropertyDescriptor(i,n):void 0})(r,t,e)}function F(r){return P({...r,state:!0,attribute:!1})}var xt="1.0.0",ct="meteoalarm-card",J="meteoalarm-card-editor",k={none:"var(--success-color, #4caf50)",minor:"var(--info-color, #43a047)",moderate:"var(--warning-color, #ffb300)",severe:"var(--meteoalarm-severe-color, #ff7043)",extreme:"var(--error-color, #f44336)"},Ft=[["wind","mdi:weather-windy"],["snow","mdi:snowflake-alert"],["ice","mdi:snowflake-alert"],["thunder","mdi:weather-lightning-rainy"],["fog","mdi:weather-fog"],["high-temp","mdi:thermometer-plus"],["high temp","mdi:thermometer-plus"],["heat","mdi:thermometer-plus"],["low-temp","mdi:thermometer-minus"],["low temp","mdi:thermometer-minus"],["cold","mdi:thermometer-minus"],["coastal","mdi:waves-arrow-up"],["fire","mdi:pine-tree-fire"],["avalanche","mdi:landslide"],["rain-flood","mdi:home-flood"],["flood","mdi:home-flood"],["rain","mdi:weather-pouring"]];function Ct(r,t){let e=`${r??""} ${t??""}`.toLowerCase();for(let[s,i]of Ft)if(e.includes(s))return i;return"mdi:alert-outline"}var Kt=[{name:"entity",required:!0,selector:{entity:{filter:[{integration:"meteoalarm_custom",domain:"sensor"}]}}},{name:"title",selector:{text:{}}},{name:"show_description",default:!0,selector:{boolean:{}}},{name:"show_instruction",selector:{boolean:{}}},{name:"compact",selector:{boolean:{}}}],Pt={en:{entity:"Entity (warning level sensor)",title:"Title",show_description:"Show warning description",show_instruction:"Show instructions",compact:"Compact mode"},lv:{entity:"Vien\u012Bba (br\u012Bdin\u0101juma l\u012Bme\u0146a sensors)",title:"Virsraksts",show_description:"R\u0101d\u012Bt br\u012Bdin\u0101juma aprakstu",show_instruction:"R\u0101d\u012Bt nor\u0101d\u012Bjumus",compact:"Kompaktais re\u017E\u012Bms"}},E=class extends u{constructor(){super(...arguments);this._computeLabel=e=>{let s=(this.hass?.locale?.language??"en").split("-")[0];return Pt[s]?.[e.name]??Pt.en[e.name]??e.name}}setConfig(e){this._config=e}_valueChanged(e){e.stopPropagation();let s=e.detail.value;this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:s},bubbles:!0,composed:!0}))}render(){return!this.hass||!this._config?h:g`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${Kt}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}};E.styles=T`
    ha-form {
      display: block;
    }
  `,$([P({attribute:!1})],E.prototype,"hass",2),$([F()],E.prototype,"_config",2),E=$([Y(J)],E);var Rt={en:{no_warnings:"No active warnings",all_clear:"All clear in",until:"until",entity_missing:"Entity not found:",entity_required:"Please set an entity of the MeteoAlarm integration",show_more:"Show details"},lv:{no_warnings:"Nav akt\u012Bvu br\u012Bdin\u0101jumu",all_clear:"Viss mier\u012Bgi:",until:"l\u012Bdz",entity_missing:"Vien\u012Bba nav atrasta:",entity_required:"Nor\u0101di MeteoAlarm integr\u0101cijas vien\u012Bbu",show_more:"R\u0101d\u012Bt deta\u013Cas"}};function j(r,t){let e=(r?.locale?.language??r?.language??"en").split("-")[0];return Rt[e]?.[t]??Rt.en[t]??t}console.info(`%c METEOALARM-CARD %c ${xt} `,"color: white; background: #e65100; font-weight: 700;","color: #e65100; background: white; font-weight: 700;");window.customCards=window.customCards??[];window.customCards.push({type:ct,name:"MeteoAlarm Card",description:"Shows active MeteoAlarm weather warnings for a region.",preview:!0,documentationURL:"https://github.com/gatisr/meteoalarm_custom"});var S=class extends u{static async getConfigElement(){return document.createElement(J)}static getStubConfig(t){return{entity:Object.values(t.states).find(s=>s.entity_id.startsWith("sensor.")&&Array.isArray(s.attributes.alerts))?.entity_id}}setConfig(t){this._config={show_description:!0,...t}}getCardSize(){return 1+(this._entity()?.attributes.alerts?.length??0)*2}shouldUpdate(t){if(t.has("_config"))return!0;let e=t.get("hass");return!e||!this._config?.entity?!0:e.states[this._config.entity]!==this.hass?.states[this._config.entity]}_entity(){if(!(!this.hass||!this._config?.entity))return this.hass.states[this._config.entity]}_title(t){if(this._config?.title)return this._config.title;let e=t?.attributes.area;return e||(t?.attributes.friendly_name??"MeteoAlarm")}_formatTime(t){if(!t)return"";let e=new Date(t);if(Number.isNaN(e.getTime()))return"";let s=this.hass?.locale?.language??"en",i=new Date().toDateString()===e.toDateString();return new Intl.DateTimeFormat(s,{...i?{}:{day:"numeric",month:"short"},hour:"2-digit",minute:"2-digit"}).format(e)}_timeRange(t){let e=this._formatTime(t.onset),s=this._formatTime(t.expires);return e&&s?`${e} \u2013 ${s}`:s?`${j(this.hass,"until")} ${s}`:e}render(){if(!this._config)return h;if(!this._config.entity)return this._warning(j(this.hass,"entity_required"));let t=this._entity();if(!t)return this._warning(`${j(this.hass,"entity_missing")} ${this._config.entity}`);let e=t.attributes.alerts??[],s=t.state in k?t.state:"none",i=k[s],n=this.hass?.formatEntityState?.(t)??t.state;return g`
      <ha-card>
        <div class="header">
          <ha-icon class="header-icon" style="color: ${i}"
            icon=${e.length?"mdi:alert-decagram":"mdi:shield-check"}
          ></ha-icon>
          <div class="name">${this._title(t)}</div>
          <div class="badge" style="background: ${i}">${n}</div>
        </div>
        ${e.length===0?g`<div class="calm">${j(this.hass,"no_warnings")}</div>`:e.map(o=>this._renderAlert(o))}
      </ha-card>
    `}_renderAlert(t){let e=k[t.severity]??k.none,s=this._config?.compact??!1;return g`
      <div class="alert" style="border-color: ${e}">
        <ha-icon icon=${Ct(t.awareness_type,t.event)} style="color: ${e}"></ha-icon>
        <div class="alert-body">
          <div class="event">${t.event??t.headline??""}</div>
          <div class="time">${this._timeRange(t)}</div>
          ${!s&&this._config?.show_description&&t.description?g`<div class="description">${t.description}</div>`:h}
          ${!s&&this._config?.show_instruction&&t.instruction?g`<div class="instruction">${t.instruction}</div>`:h}
        </div>
      </div>
    `}_warning(t){return g`<ha-card><div class="calm">${t}</div></ha-card>`}};S.styles=T`
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
      color: #fff;
      border-radius: 12px;
      padding: 3px 10px;
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
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
    }
    .instruction {
      color: var(--secondary-text-color);
      font-style: italic;
    }
  `,$([P({attribute:!1})],S.prototype,"hass",2),$([F()],S.prototype,"_config",2),S=$([Y(ct)],S);export{S as MeteoAlarmCard};
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
