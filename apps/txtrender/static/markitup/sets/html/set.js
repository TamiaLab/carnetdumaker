// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
mySettings = {
	onShiftEnter:	{keepDefault:false, replaceWith:'[br]\n'},
	onCtrlEnter:	{keepDefault:false, openWith:'\n\n', closeWith:'\n\n'},
	onTab:			{keepDefault:false, openWith:'    '},
    resizeHandle:   true,
    previewPosition:    'before',
    previewParserPath : '/api/texte/preview/',
    previewParserVar :  'content',
	markupSet: [
        {name:'Titre', dropMenu: [
            {name:'Titre de niveau 1', key:'1', openWith:'[h1]', closeWith:'[/h1]', placeHolder:'Votre titre ici', className:'bbheader' },
            {name:'Titre de niveau 2', key:'2', openWith:'[h2]', closeWith:'[/h2]', placeHolder:'Votre titre ici', className:'bbheader' },
            {name:'Titre de niveau 3', key:'3', openWith:'[h3]', closeWith:'[/h3]', placeHolder:'Votre titre ici', className:'bbheader' },
            {name:'Titre de niveau 4', key:'4', openWith:'[h4]', closeWith:'[/h4]', placeHolder:'Votre titre ici', className:'bbheader' },
            {name:'Titre de niveau 5', key:'5', openWith:'[h5]', closeWith:'[/h5]', placeHolder:'Votre titre ici', className:'bbheader' },
            {name:'Titre de niveau 6', key:'6', openWith:'[h6]', closeWith:'[/h6]', placeHolder:'Votre titre ici', className:'bbheader' }
        ], className:'bbheader'},

        {separator:'---------------' },
        {name:'Code', dropMenu: [
            {name:'Code (bloc)', key:'#', openWith:'[code]', closeWith:'[/code]', placeHolder:'Votre code ici', className:'bbcode' },
            {name:'Code (ligne)', openWith:'[icode]', closeWith:'[/icode]', placeHolder:'Votre code ici', className:'bbcode' },
            {name:'Code Python', openWith:'[python]', closeWith:'[/python]', placeHolder:'Votre code Python ici', className:'bbcode' },
            {name:'Code C/C++', openWith:'[cpp]', closeWith:'[/cpp]', placeHolder:'Votre code C/C++ ici', className:'bbcode' },
            {name:'Code Java', openWith:'[java]', closeWith:'[/java]', placeHolder:'Votre code Java ici', className:'bbcode' },
            {name:'Code HTML', openWith:'[html]', closeWith:'[/html]', placeHolder:'Votre code HTML ici', className:'bbcode' },
            {name:'Code PHP', openWith:'[php]', closeWith:'[/php]', placeHolder:'Votre code PHP ici', className:'bbcode' }
        ], className:'bbcode'},

        {separator:'---------------' },
        {name:'Spoiler', dropMenu: [
            {name:'Spoiler (bloc)', openWith:'[spoiler]', closeWith:'[/spoiler]', placeHolder:'Votre texte caché ici', className:'bbspoiler' },
            {name:'Spoiler (ligne)', openWith:'[ispoiler]', closeWith:'[/ispoiler]', placeHolder:'Votre texte caché ici', className:'bbspoiler' }
        ], className:'bbspoiler'},

		{separator:'---------------' },
        {name:'Mise en forme', dropMenu: [
		    {name:'Gras', key:'B', openWith:'[b]', closeWith:'[/b]', placeHolder:'Votre texte en gras ici', className:'bbbold' },
		    {name:'Italic', key:'I', openWith:'[i]', closeWith:'[/i]', placeHolder:'Votre texte italique ici', className:'bbitalic' },
		    {name:'Souligné', key:'U', openWith:'[u]', closeWith:'[/u]', placeHolder:'Votre texte souligné ici', className:'bbunderline' },
		    {name:'Barré', key:'S', openWith:'[s]', closeWith:'[/s]', placeHolder:'Votre texte barré ici', className:'bbstrikethrough' },
		    {name:'Exposant', openWith:'[sup]', closeWith:'[/sup]', placeHolder:'Votre texte en exposant ici', className:'bbsuperscript' },
		    {name:'Indice', openWith:'[sub]', closeWith:'[/sub]', placeHolder:'Votre texte en indice ici', className:'bbsubscript' }
        ], className:'bbformat'},

        {separator:'---------------' },
        {name:'Alignement', dropMenu: [
		    {name:'Centrer', openWith:'[center]', closeWith:'[/center]', placeHolder:'Votre texte centré ici', className:'bbcenter' },
		    {name:'Droite', openWith:'[right]', closeWith:'[/right]', placeHolder:'Votre texte à droite ici', className:'bbright' },
		    {name:'Gauche', openWith:'[left]', closeWith:'[/left]', placeHolder:'Votre texte à gauche ici', className:'bbleft' }
        ], className:'bbalign'},

		{separator:'---------------' },
        {name:'Liste', dropMenu: [
            {name:'Liste non ordonnée', openWith:'[ul]\n', closeWith:'[/ul]\n', className:'bbul' },
            {name:'Liste ordonnée', openWith:'[ol]\n', closeWith:'[/ol]\n', className:'bbol' },
            {name:'Element de liste', openWith:'[li]', closeWith:'[/li]', placeHolder:'Votre texte ici', className:'bbli' }
        ], className:'bblist'},

        {separator:'---------------' },
        {name:'Tableau', dropMenu: [
            {name:'Tableau', openWith:'[table]\n', closeWith:'[/table]\n', className:'bbtable' },
		    {name:'Ligne de tableau', openWith:'[tr]\n', closeWith:'[/tr]\n', className:'bbtr' },
		    {name:'Entête de colonne', openWith:'[th]', closeWith:'[/th]', placeHolder:'Votre entête de colonne ici', className:'bbth' },
		    {name:'Cellule de tableau', openWith:'[td]', closeWith:'[/td]', placeHolder:'Votre texte de cellule ici', className:'bbth' }
        ], className:'bbtable'},

		{separator:'---------------' },
		{name:'Image', replaceWith:'[img alt="[![Texte alternatif]!]"][![Source:!:http://]!][/img]', className:'bbpicture' },

        {separator:'---------------' },
		{name:'Lien', openWith:'[url="[![Lien:!:http://]!]"]', closeWith:'[/url]', placeHolder:'Le texte de votre lien', className:'bblink' },

        {separator:'---------------' },
        {name:'Image', replaceWith:'[youtube][![Lien youtube:!:https://]!][/youtube]', className:'bbyoutube' },

        {separator:'---------------' },
        {name:'Divers', dropMenu: [
            {name:'Raccourci clavier', openWith:'[kbd]', closeWith:'[/kbd]', placeHolder:'Votre raccourci ici', className:'bbkeyboard' },
            {name:'Texte petite taille', openWith:'[small]', closeWith:'[/small]', placeHolder:'Votre texte en petite taille ici', className:'bbsmall' },
            {name:'Citation longue', openWith:'[quote]', closeWith:'[/quote]', placeHolder:'Votre citation longue ici', className:'bbquote' }
        ], className:'bbmisc'},

		{separator:'---------------' },
		{name:'Prévisualisation', className:'preview', call:'preview' }
	]
}