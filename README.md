# Fix Ninja Forms + WPML — Traduction anglaise des formulaires

## Le problème

Les formulaires Ninja Forms restent en français quand WPML passe en anglais, alors que l'espagnol et le néerlandais fonctionnent correctement.

## La solution

Un **mu-plugin** WordPress qui intercepte l'affichage des formulaires Ninja Forms et force l'application des traductions WPML sur tous les champs (labels, placeholders, options, messages, HTML, etc.).

## Installation (2 minutes)

### Option 1 — mu-plugin (recommandé)

1. Copier le fichier `fix-ninjaforms-wpml-english.php` dans :
   ```
   wp-content/mu-plugins/fix-ninjaforms-wpml-english.php
   ```
   Si le dossier `mu-plugins` n'existe pas, le créer.

2. C'est tout. Le mu-plugin se charge automatiquement, pas besoin de l'activer.

### Option 2 — Plugin classique

1. Copier le fichier `fix-ninjaforms-wpml-english.php` dans :
   ```
   wp-content/plugins/fix-ninjaforms-wpml-english.php
   ```

2. Aller dans **Extensions** dans l'admin WordPress et activer **Fix Ninja Forms WPML English Translation**.

### Option 3 — Code snippet dans functions.php

1. Ouvrir le fichier `functions.php` du thème enfant actif.
2. Coller tout le contenu de `fix-ninjaforms-wpml-english.php` à la fin du fichier (sans le tag `<?php` d'ouverture si `functions.php` en a déjà un).

## Vérification

1. Vider tous les caches (WPML > Support > vider les caches, + cache serveur/plugin de cache).
2. Aller sur le site en mode anglais.
3. Les formulaires doivent maintenant afficher les traductions anglaises.

## Ce que le fix traduit

- Labels des champs
- Placeholders
- Valeurs par défaut
- Textes d'aide / descriptions
- Options des select / radio / checkbox
- Champs HTML
- Titre du formulaire
- Message de succès
- Messages d'erreur du formulaire

## Pré-requis

- WordPress
- WPML + WPML String Translation (actifs)
- Ninja Forms (actif)
- Les traductions anglaises doivent exister dans WPML > Traduction des chaînes

## Désinstallation

Supprimer le fichier du dossier `mu-plugins` (ou désactiver le plugin / retirer le code de `functions.php`).
