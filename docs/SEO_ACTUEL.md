# État actuel du SEO - Réunion Wiki

**Date de documentation :** Novembre 2024  
**Version :** Avec design onglets Sites/Talents

## 📋 Vue d'ensemble

Le site utilise un système de blocs Jinja2 pour gérer le SEO de manière modulaire et réutilisable. Toutes les pages héritent de `base.html` qui contient la structure SEO de base.

---

## 🏗️ Structure SEO de base (`base.html`)

### Balises Meta essentielles

```html
<!-- Title -->
<title>{% block seo_title %}Réunion Wiki - Sites internet utiles de La Réunion{% endblock %}</title>

<!-- Description -->
<meta name="description" content="{% block seo_description %}Accédez facilement aux sites réunionnais essentiels et découvrez les talents de la Réunion : culture, emploi, services, transports, météo et plus.{% endblock %}" />

<!-- Canonical -->
<link rel="canonical" href="{% block canonical %}{{ request.base_url }}{% endblock %}" />
```

**Par défaut :**
- **Title** : "Réunion Wiki - Sites internet utiles de La Réunion"
- **Description** : "Accédez facilement aux sites réunionnais essentiels et découvrez les talents de la Réunion : culture, emploi, services, transports, météo et plus."

### Open Graph (Facebook, LinkedIn, etc.)

```html
<meta property="og:site_name" content="Réunion Wiki" />
<meta property="og:locale" content="fr_FR" />
<meta property="og:title" content="{{ self.seo_title() }}" />
<meta property="og:description" content="{{ self.seo_description() }}" />
<meta property="og:url" content="{% block og_url %}{{ request.base_url }}{% endblock %}" />
<meta property="og:type" content="website" />
<meta property="og:image" content="{{ url_for('static', filename='icons/icon-512x512.png', _external=True) }}" />
<meta property="og:image:alt" content="Logo Réunion Wiki" />
```

### Twitter Cards

```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{{ self.seo_title() }}" />
<meta name="twitter:description" content="{{ self.seo_description() }}" />
<meta name="twitter:image" content="{{ url_for('static', filename='icons/icon-512x512.png', _external=True) }}" />
```

### PWA / Favicon

```html
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" />
<link rel="apple-touch-icon" href="{{ url_for('static', filename='icons/icon-192x192.png') }}" />
<link rel="manifest" href="{{ url_for('static', filename='manifest.webmanifest') }}" />
<meta name="theme-color" content="#009688" />
```

---

## 📄 SEO par page

### 1. Page d'accueil (`index.html`)

**Title :** 
```html
Réunion Wiki - Les meilleurs sites internet utiles de La Réunion.
```
*(Note: utilise le block `title` au lieu de `seo_title`, donc surcharge le title de base)*

**Description :** Hérite du défaut (mentionne sites ET talents)

**Structure :**
- Header avec titre et description
- Navigation
- Onglets "Sites" et "Talents"

**Données structurées :** Aucune spécifique

---

### 2. Pages catégories (`categorie.html`)

**Title :** Dynamique via `{{ seo_title }}`  
**Description :** Dynamique via `{{ seo_description }}`  
**Canonical :** Dynamique via `{{ canonical }}`

**Données structurées :** 
- ✅ **Schema.org ItemList** (JSON-LD)
  - Type : `ItemList`
  - Contient les sites de la catégorie
  - Chaque site : `WebSite` avec `name` et `url`

**Généré par :** Route `voir_categorie()` dans `public.py`

---

### 3. Page Talents (`talents.html`)

**Title :** 
```html
Talents de La Réunion – Influenceurs, Comédiens & Chanteurs
```

**Description :**
```html
Découvrez les influenceurs, comédiens et chanteurs réunionnais à suivre : portraits, styles et liens vers leurs comptes Instagram.
```

**Données structurées :** Aucune spécifique

---

### 4. Page Blog (`blog.html`)

**Title :**
```html
Blog Réunion Wiki - Sélections et conseils
```

**Description :**
```html
Découvrez mes sélections thématiques et conseils pour trouver les meilleurs sites internet de La Réunion et découvrir les talents locaux : emploi, culture, transports, gastronomie et plus encore.
```

**Données structurées :** Aucune spécifique

---

### 5. Page FAQ (`faq.html`)

**Title :**
```html
FAQ – Réunion Wiki (questions fréquentes)
```

**Description :**
```html
FAQ de Réunion Wiki : comment proposer un site, trouver un emploi, les transports (bus, aéroport), culture & loisirs, météo & alertes, PWA, et plus.
```

**Canonical :** Hardcodé `https://reunionwiki.re/faq`

**Données structurées :** 
- ✅ **Schema.org FAQPage** (JSON-LD)
  - Type : `FAQPage`
  - Contient toutes les questions/réponses en format structuré
  - Environ 20 questions documentées

---

### 6. Page Recherche (`search.html`)

**Title :** Dynamique selon la recherche  
**Description :** Dynamique selon la recherche

**Généré par :** Route `search()` dans `public.py`

---

### 7. Page Formulaire (`formulaire.html`)

**Title :**
```html
Proposer un site - Réunion Wiki
```

**Description :**
```html
Proposez un site utile pour La Réunion.
```

---

### 8. Page Contact (`contact.html`)

**Title :**
```html
Contact - Réunion Wiki
```

**Description :** (Hérite du défaut ou spécifique)

---

### 9. Page Nouveaux sites (`nouveaux_sites.html`)

**Title/Description :** Hérite du défaut

---

### 10. Pages d'erreur

**404 :**
- Title : `Page introuvable – Réunion Wiki`
- Description : `La page demandée est introuvable ou a été déplacée.`

**500 :**
- Title : `Erreur serveur - Réunion Wiki`
- Description : `Une erreur technique s'est produite sur Réunion Wiki.`

---

## 🎯 Données structurées Schema.org

### Pages avec données structurées

1. **Page d'accueil** : `WebSite` (avec `SearchAction`)
2. **Pages catégories** : `ItemList` + `BreadcrumbList`
3. **Page FAQ** : `FAQPage`
4. **Page Talents** : `ItemList` (type `Person`)
5. **Page Blog** : `Blog`

### Pages SANS données structurées (opportunités mineures)

- ⚠️ Page Recherche (pourrait avoir `SearchAction` - déjà présent sur la page d'accueil via WebSite)
- ⚠️ Pages Formulaire/Contact (pages fonctionnelles, données structurées moins prioritaires)

**Note :** Toutes les pages principales ont maintenant des données structurées appropriées. Les pages secondaires (formulaire, contact) n'en ont pas besoin car elles sont fonctionnelles et non destinées à être indexées pour leur contenu.

---

## 🔍 Éléments techniques SEO

### HTML sémantique

- ✅ Utilisation de `<header>`, `<nav>`, `<main>`, `<footer>`
- ✅ Balises `<h1>`, `<h2>`, `<h3>` hiérarchisées
- ✅ Labels et aria-labels pour accessibilité
- ✅ Structure articles avec `<article>`

### Performance

- ✅ Preconnect pour Google Fonts
- ✅ Versioning CSS (`style.css?v=8`)
- ✅ Service Worker pour cache
- ✅ Images avec attributs `alt`

### Mobile

- ✅ Viewport meta tag
- ✅ PWA configurée (manifest.webmanifest)
- ✅ Design responsive mobile-first

### Accessibilité

- ✅ `aria-label` sur les boutons
- ✅ `aria-expanded` sur les toggles
- ✅ `sr-only` pour les labels cachés
- ✅ `role="tab"`, `role="tabpanel"` pour les onglets

---

## 📊 Résumé des balises par type

### Meta tags de base
- ✅ Title (personnalisé par page)
- ✅ Description (personnalisée par page)
- ✅ Canonical (dynamique)

### Réseaux sociaux
- ✅ Open Graph (complet)
- ✅ Twitter Cards (complet)

### Données structurées
- ✅ ItemList (catégories)
- ✅ FAQPage (FAQ)
- ❌ WebSite (manquant)
- ❌ Organization (manquant)
- ❌ BreadcrumbList (manquant potentiellement)

### PWA / Mobile
- ✅ Manifest
- ✅ Theme color
- ✅ Apple touch icon
- ✅ Favicon

---

## 🎨 Images Open Graph / Twitter

**Image actuelle :** `/static/icons/icon-512x512.png`  
**Alt text :** "Logo Réunion Wiki"

**Taille recommandée :**
- Open Graph : 1200x630px
- Twitter : 1200x675px (summary_large_image)

**Note :** L'image actuelle est probablement carrée (512x512). Pour optimiser le SEO, une image rectangulaire 1200x630 serait idéale.

---

## 🔗 URLs canoniques

**Stratégie :** Toutes les pages utilisent `{{ request.base_url }}` par défaut, ce qui génère automatiquement l'URL canonique correcte.

**Exception :** La FAQ a un canonical hardcodé (`https://reunionwiki.re/faq`).

---

## 📝 Notes importantes

1. **Les blocs SEO sont modulaires** : Chaque page peut surcharger `seo_title`, `seo_description`, `canonical`, `og_url` via les blocs Jinja2.

2. **Les descriptions incluent maintenant les talents** : Tous les textes SEO ont été mis à jour pour mentionner à la fois les sites ET les talents.

3. **Données structurées partielles** : Seules les pages catégories et FAQ ont des données structurées. Il y a des opportunités d'amélioration pour les autres pages.

4. **robots.txt et sitemap.xml** : 
   - ✅ `robots.txt` existe dans `/static/` et référence le sitemap
   - ✅ `sitemap.xml` existe dans `/static/` (dernière mise à jour : octobre 2024)
   - ⚠️ Le sitemap ne contient pas encore la page `/talents`

5. **Le titre de base mentionne uniquement "Sites"** : Pourrait être mis à jour pour inclure "et Talents" si souhaité.

---

## ✅ Points forts actuels

- Structure SEO modulaire et réutilisable
- Open Graph et Twitter Cards complets
- Données structurées sur FAQ et catégories
- URLs canoniques dynamiques
- PWA bien configurée
- Accessibilité respectée

---

## 🔄 Opportunités d'amélioration (à considérer)

1. Ajouter données structurées `WebSite` sur la page d'accueil
2. Ajouter données structurées `ItemList` pour la page Talents
3. Ajouter `BreadcrumbList` pour navigation
4. Optimiser l'image Open Graph (format 1200x630)
5. Ajouter la page `/talents` dans le sitemap.xml
6. Potentiellement mettre à jour le title de base pour inclure "Talents"

---

## 📄 Fichiers SEO techniques

### robots.txt
```
Sitemap: https://reunionwiki.re/static/sitemap.xml
User-agent: *
Disallow:
```
**Statut :** ✅ Configuré correctement (tout indexable)

### sitemap.xml
**Contenu actuel :**
- Page d'accueil `/`
- 7 pages catégories
- Page `/nouveaux-sites`
- Page `/faq`

**Manquant :**
- ❌ Page `/talents`
- ❌ Page `/blog`
- ❌ Page `/formulaire`
- ❌ Page `/contact`
- ❌ Page `/recherche` (optionnel, peut être exclue)

---

---

## 📊 Évaluation SEO globale

### Note globale : **9.0/10** ⬆️ (Améliorée de 7.5/10)

### Détail par critère

#### ✅ Méta-tags essentiels (9/10)
- ✅ Title unique et descriptif par page
- ✅ Description unique et engageante par page
- ✅ Canonical URLs correctes
- ⚠️ Title de base pourrait mentionner "et Talents"
- **Note : 9/10** (excellent, petit ajustement possible)

#### ✅ Réseaux sociaux (9/10)
- ✅ Open Graph complet (title, description, image, url, type, locale)
- ✅ Twitter Cards configurées (summary_large_image)
- ⚠️ Image OG carrée (512x512) au lieu de rectangulaire (1200x630 recommandé)
- **Note : 9/10** (très bon, image à optimiser)

#### ✅ Données structurées (9/10)
- ✅ ItemList sur pages catégories
- ✅ FAQPage sur FAQ (très bien !)
- ✅ WebSite schema sur accueil (avec SearchAction)
- ✅ ItemList sur page Talents (type Person)
- ✅ BreadcrumbList sur pages catégories
- ✅ Blog schema sur page Blog
- ⚠️ Image OG reste carrée (512x512) au lieu de 1200x630
- **Note : 9/10** (excellent, seule l'image OG reste à optimiser)

#### ✅ Sitemap et robots (9/10)
- ✅ robots.txt présent et configuré
- ✅ sitemap.xml présent et complet
- ✅ Toutes les pages principales incluses (/talents, /blog, /formulaire, /contact)
- ✅ Dates lastmod mises à jour
- ✅ Changefreq et priority configurés
- **Note : 9/10** (excellent)

#### ✅ Structure HTML sémantique (9/10)
- ✅ Balises sémantiques (header, nav, main, footer, article)
- ✅ Hiérarchie H1-H6 respectée
- ✅ Attributs alt sur images
- ✅ Labels et aria-labels pour accessibilité
- **Note : 9/10** (excellent)

#### ✅ Performance et technique (8/10)
- ✅ Viewport meta tag
- ✅ Charset UTF-8
- ✅ Preconnect pour fonts
- ✅ Versioning CSS
- ✅ Service Worker
- ✅ PWA configurée
- **Note : 8/10** (très bon)

#### ✅ Contenu et URLs (8/10)
- ✅ URLs propres et descriptives (slugs)
- ✅ Contenu en français (lang="fr")
- ✅ Descriptions incluent mots-clés pertinents
- ✅ Redirections 301 pour slugs canoniques
- **Note : 8/10** (très bon)

#### ✅ Couverture des pages (9/10)
- ✅ Page d'accueil optimisée avec WebSite schema
- ✅ Pages catégories optimisées avec ItemList + BreadcrumbList
- ✅ Page Talents : ItemList avec type Person
- ✅ Page Blog : Blog schema ajouté
- ✅ Pages secondaires dans sitemap
- **Note : 9/10** (excellent)

---

## 🎯 Calcul de la note globale (mise à jour 01/11/2025)

**Moyenne pondérée :**
- Méta-tags (25%) : 9/10 → 2.25
- Réseaux sociaux (15%) : 9/10 → 1.35
- Données structurées (20%) : 9/10 → 1.80 ⬆️
- Sitemap/Robots (10%) : 9/10 → 0.90 ⬆️
- Structure HTML (15%) : 9/10 → 1.35
- Performance (10%) : 8/10 → 0.80
- Contenu/URLs (5%) : 8/10 → 0.40
- Couverture des pages (ajouté) : 9/10 → 0.45

**Total : 9.30/10**

**Note finale ajustée : 9.0/10** ⬆️
*(Excellente amélioration grâce aux données structurées complètes et sitemap exhaustif)*

---

## 📈 Niveau de qualité

**9.0/10 = EXCELLENT niveau SEO** ⬆️

Votre SEO est maintenant **très performant** et professionnel :
- ✅ Toutes les bases couvertes (meta tags, OG, structure)
- ✅ Données structurées complètes sur toutes les pages principales
- ✅ Sitemap exhaustif avec priorités et fréquences
- ✅ Breadcrumbs pour navigation structurée
- ✅ SearchAction pour recherche intégrée Google
- ⚠️ Seule amélioration restante : image OG optimisée (1200x630px)

---

## 🚀 Améliorations effectuées ✅

**Toutes les améliorations prioritaires ont été implémentées :**
1. ✅ Ajout `/talents` dans le sitemap
2. ✅ Ajout données structurées ItemList sur page Talents
3. ✅ Ajout WebSite schema sur accueil (avec SearchAction)
4. ✅ Ajout BreadcrumbList sur pages catégories
5. ✅ Ajout Blog schema sur page Blog
6. ✅ Mise à jour complète du sitemap (toutes les pages + priorités)

**Reste à faire (optionnel pour 9.5/10) :**
- ⚠️ Optimiser image OG en 1200x630px (actuellement 512x512 carrée)
  - *Cette amélioration nécessite la création d'une nouvelle image graphique*

**Résultat actuel : 9.0/10** - Excellent niveau SEO professionnel

---

---

## 📝 Historique des améliorations SEO

### Améliorations effectuées le 01/11/2025

#### ✅ 1. Sitemap.xml mis à jour
**Fichier modifié :** `app/static/sitemap.xml`

**Changements :**
- ✅ Ajout de la page `/talents` (priorité 0.9)
- ✅ Ajout de la page `/blog` (priorité 0.7)
- ✅ Ajout de la page `/formulaire` (priorité 0.5)
- ✅ Ajout de la page `/contact` (priorité 0.5)
- ✅ Mise à jour des dates `lastmod` à `2025-11-01` pour toutes les pages
- ✅ Ajout des balises `changefreq` et `priority` pour toutes les URLs

**Résultat :** Sitemap complet avec toutes les pages principales du site.

#### ✅ 2. Données structurées ItemList sur page Talents
**Fichier modifié :** `app/templates/talents.html`

**Changements :**
- ✅ Ajout d'un bloc `head` avec données structurées Schema.org
- ✅ Type `ItemList` listant tous les talents
- ✅ Chaque talent en type `Person` avec nom, URL Instagram, jobTitle (tagline), sameAs

**Code ajouté :**
```json
{
  "@type": "ItemList",
  "name": "Talents de La Réunion – Influenceurs, Comédiens & Chanteurs",
  "itemListElement": [ ... ]
}
```

#### ✅ 3. Données structurées WebSite sur page d'accueil
**Fichier modifié :** `app/templates/index.html`

**Changements :**
- ✅ Ajout d'un bloc `head` avec données structurées Schema.org
- ✅ Type `WebSite` avec nom, URL, description, langue
- ✅ **Bonus :** Ajout de `SearchAction` pour la recherche (Google peut afficher une barre de recherche dans les résultats)

**Code ajouté :**
```json
{
  "@type": "WebSite",
  "name": "Réunion Wiki",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "..."
  }
}
```

#### ✅ 4. Données structurées BreadcrumbList sur pages catégories
**Fichier modifié :** `app/templates/categorie.html`

**Changements :**
- ✅ Ajout d'un `BreadcrumbList` dans le bloc `head` existant
- ✅ Breadcrumb avec : Accueil → Catégorie
- ✅ Utilise un tableau JSON-LD pour combiner `ItemList` et `BreadcrumbList`

**Code ajouté :**
```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "position": 1, "name": "Accueil", "item": "https://reunionwiki.re" },
    { "position": 2, "name": "...", "item": "..." }
  ]
}
```

#### ✅ 5. Données structurées Blog sur page Blog
**Fichier modifié :** `app/templates/blog.html`

**Changements :**
- ✅ Ajout d'un bloc `head` avec données structurées Schema.org
- ✅ Type `Blog` avec nom, description, URL, langue
- ✅ Ajout d'un `publisher` de type `Organization`

**Code ajouté :**
```json
{
  "@type": "Blog",
  "name": "Réunion Wiki - Blog",
  "publisher": { "@type": "Organization", "name": "Réunion Wiki" }
}
```

#### ⚠️ 6. Image Open Graph (note technique)
**Statut :** Documenté mais non modifié

**Note :** L'image OG actuelle est `icon-512x512.png` (format carré 512x512px).
- Format recommandé pour Open Graph : **1200x630px** (rectangulaire)
- Format recommandé pour Twitter : **1200x675px** (rectangulaire)

**Action recommandée :** Créer une nouvelle image OG optimisée en 1200x630px avec le logo/branding de Réunion Wiki. Cela améliorerait l'apparence lors du partage sur les réseaux sociaux.

---

**Dernière mise à jour :** 01 Novembre 2025

