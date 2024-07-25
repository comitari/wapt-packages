# Tutoriel pour soumettre une demande d'upload de paquets sur le Github Communautaire de Comitari

Ce tutoriel vous guide à travers les étapes pour soumettre une demande d'upload de code sur notre dépot en utilisant une pull request.

## Étape 1: Forker le dépôt

1. **Accédez au dépôt GitHub:**
   - Ouvrez votre navigateur et allez sur la page du dépôt GitHub où vous souhaitez soumettre du code.

2. **Forker le dépôt:**
   - Cliquez sur le bouton "Fork" en haut à droite de la page du dépôt. Cela créera une copie du dépôt dans votre propre compte GitHub.

## Étape 2: Cloner le dépôt forké

1. **Cloner le dépôt forké:**
   - Allez sur la page de votre dépôt forké.
   - Cliquez sur le bouton "Code" et copiez l'URL du dépôt.
   - Ouvrez un terminal et exécutez la commande suivante pour cloner le dépôt sur votre machine locale:
     ```sh
     git clone https://github.com/votre-utilisateur/nom-du-depot.git
     cd nom-du-depot
     ```

## Étape 3: Créer une nouvelle branche

1. **Créer une nouvelle branche:**
   - Il est recommandé de créer une nouvelle branche pour vos modifications. Cela permet de garder le code principal intact.
     ```sh
     git checkout -b ma-nouvelle-branche
     ```

## Étape 4: Faire des modifications

1. **Modifier les fichiers:**
   - Apportez les modifications nécessaires aux fichiers du projet.

2. **Ajouter les modifications:**
   - Ajoutez les fichiers modifiés à l'index Git:
     ```sh
     git add .
     ```

3. **Faire un commit:**
   - Faites un commit de vos modifications avec un message descriptif:
     ```sh
     git commit -m "Description des modifications"
     ```

## Étape 5: Pousser les modifications

1. **Pousser les modifications vers GitHub:**
   - Poussez votre nouvelle branche vers votre dépôt forké sur GitHub:
     ```sh
     git push origin ma-nouvelle-branche
     ```

## Étape 6: Créer une pull request

1. **Accédez à votre dépôt forké sur GitHub:**
   - Ouvrez votre navigateur et allez sur la page de votre dépôt forké.

2. **Créer une pull request:**
   - Vous devriez voir un message vous invitant à créer une pull request pour la branche que vous venez de pousser. Cliquez sur "Compare & pull request".
   - Remplissez le formulaire de pull request avec un titre et une description détaillée de vos modifications.
   - Cliquez sur "Create pull request".

## Étape 7: Attendre la revue

1. **Attendre la revue:**
   - Les mainteneurs du dépôt original recevront une notification de votre pull request. Ils examineront vos modifications et pourront vous demander des ajustements ou des clarifications.

2. **Apporter des modifications si nécessaire:**
   - Si des modifications sont demandées, vous pouvez les apporter dans votre branche locale, puis les pousser à nouveau vers GitHub. Les modifications seront automatiquement ajoutées à la pull request existante.

## Étape 8: Merge de la pull request

1. **Merge de la pull request:**
   - Une fois que vos modifications sont approuvées, les mainteneurs du dépôt original fusionneront votre pull request dans le dépôt principal.

Félicitations ! Vous avez soumis une demande d'upload de code sur GitHub en utilisant une pull request.
