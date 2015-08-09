// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
mySettings = {
	onShiftEnter:	{keepDefault:false, replaceWith:'<br />\n'},
	onCtrlEnter:	{keepDefault:false, openWith:'\n<p>', closeWith:'</p>\n'},
	onTab:			{keepDefault:false, openWith:'	 '},
    resizeHandle:   true,
    previewPosition:    'before',
    previewParserPath : '/api/texte/preview/',
    previewParserVar :  'content',
	markupSet: [
		{name:'Titre de niveau 1', key:'1', openWith:'<h1(!( class="[![Class]!]")!)>', closeWith:'</h1>', placeHolder:'Votre titre ici', className:'h1' },
		{name:'Titre de niveau 2', key:'2', openWith:'<h2(!( class="[![Class]!]")!)>', closeWith:'</h2>', placeHolder:'Votre titre ici', className:'h2' },
		{name:'Titre de niveau 3', key:'3', openWith:'<h3(!( class="[![Class]!]")!)>', closeWith:'</h3>', placeHolder:'Votre titre ici', className:'h3' },
		{name:'Titre de niveau 4', key:'4', openWith:'<h4(!( class="[![Class]!]")!)>', closeWith:'</h4>', placeHolder:'Votre titre ici', className:'h4' },
		{name:'Titre de niveau 5', key:'5', openWith:'<h5(!( class="[![Class]!]")!)>', closeWith:'</h5>', placeHolder:'Votre titre ici', className:'h5' },
		{name:'Titre de niveau 6', key:'6', openWith:'<h6(!( class="[![Class]!]")!)>', closeWith:'</h6>', placeHolder:'Votre titre ici', className:'h6' },
		{name:'Paragraphe', openWith:'<p(!( class="[![Class]!]")!)>', closeWith:'</p>', className:'paragraph' },
		{separator:'---------------' },
		{name:'Gras', key:'B', openWith:'(!(<strong>|!|<b>)!)', closeWith:'(!(</strong>|!|</b>)!)', className:'bold' },
		{name:'Italic', key:'I', openWith:'(!(<em>|!|<i>)!)', closeWith:'(!(</em>|!|</i>)!)', className:'italic' },
		//{name:'Souligné', key:'S', openWith:'<ins>', closeWith:'</ins>', className:'underline' },
		{name:'Barré', key:'S', openWith:'<del>', closeWith:'</del>', className:'stroke' },
		{separator:'---------------' },
		{name:'Liste non ordonnée', openWith:'<ul>\n', closeWith:'</ul>\n', className:'ul' },
		{name:'Liste ordonnée', openWith:'<ol>\n', closeWith:'</ol>\n', className:'ol' },
		{name:'Element de liste', openWith:'<li>', closeWith:'</li>', className:'li' },
		{separator:'---------------' },
		{name:'Image', key:'P', replaceWith:'<img src="[![Source:!:http://]!]" alt="[![Texte alternatif]!]" />', className:'img' },
		{name:'Lien', key:'L', openWith:'<a href="[![Lien:!:http://]!]"(!( title="[![Titre]!]")!)>', closeWith:'</a>', placeHolder:'Le texte de votre lien', className:'link' },
		{separator:'---------------' },
		{name:'Supprimer les balises', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } },
		{name:'Prévisualisation', className:'preview', call:'preview' }
	]
}