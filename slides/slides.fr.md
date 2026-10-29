# Harness vs Loop

Deux stratégies pour des agents IA qui marchent vraiment

Yacine

---

# Yacine Touati

Software architect – agents autonomes & architectures LLM

| 2008 – 2018 | 2018 – 2025 | Depuis 2025 |
|---|---|---|
| **Armée de Terre** | **Développeur** | **CTO de LAMALO** |
| Traducteur arabe / français / anglais, chef de groupe | Full stack, sites à très fort trafic, conseil | Moteur IA multi-fournisseurs en production |

Formateur et mentor : Udacity, OpenClassrooms, Wild Code School

linkedin.com/in/yactouat

> **Notes :** Se présenter en une phrase par période.

---

# Au programme

1. Ce qu'est un agent : un modèle et un harness
2. Pourquoi un agent échoue, et comment le réparer
3. 11 questions à poser avant de s'embarquer dans un projet agentique
4. Comment vous pouvez déjà améliorer vos agents

Ensuite : 30 minutes de code en direct, où l'on construit notre propre agent.

> **Notes :** Annoncer le format : 30 minutes de talk, 30 minutes de code en direct, puis un verre.

---

# Ce n'est pas le modèle

« Ce n'est pas le modèle, c'est ce que vous voulez, et la façon dont c'est spécifié et construit, qui fait la différence. »

> **Notes :** C'est l'idée à retenir. Tout le reste du talk sert à la prouver, et on la répétera à la fin.

---

# Mental model pour qualifier un agent

Un programme qui :

1. **comprend** des entrées non structurées, comme le langage naturel ;
2. **connaît son environnement**, grâce à des connecteurs vers des systèmes externes ;
3. **prend des décisions** de façon autonome.

> **Notes :** Si l'un des trois manque, ce n'est pas un agent. On reviendra sur ce test à la fin, avec la question « vrai agent ou glorified chatbot ? ».

---

# Définition formelle d'un agent = modèle + harness

Tout ce qui n'est pas le modèle, c'est le harness. C'est aussi simple que ça

Schéma : le modèle au centre, entouré de quatre blocs : **outils**, **données**, **règles**, **loop**.

> **Notes :** Le modèle, c'est le cerveau : GPT, Claude, Gemini… Le harness, c'est tout le reste. La formule vient de LangChain, et la plupart des acteurs du secteur la reprennent.

---

# Les cinq sous-systèmes d'un bon harness

| | |
|---|---|
| **Instructions** | Ce que l'agent doit faire, et comment. |
| **Outils** | Les actions à sa disposition. |
| **Environnement** | Un contexte d'exécution prévisible. |
| **État** | Ce que la session suivante pourra relire. |
| **Feedback** | Les signaux qui vérifient le travail. |

Un harness n'est pas un simple système de fichiers : c'est l'interaction entre ces cinq sous-systèmes.

Source : hands-on-harness-engineering.com

> **Notes :** Thoughtworks donne presque la même liste : le harness apporte à l'agent « le contexte, les outils, les règles, l'état et le feedback » dont il a besoin. La vérification du travail fait donc partie du harness.

---

# Le harness

Tout ce qui entoure le modèle :

- ses **outils** ;
- les **systèmes et données** auxquels il a accès ;
- les **règles** à respecter ;
- sa **façon de travailler** : la loop.

> **Notes :** Penser à un nouveau collègue. Sans les bons accès et les bonnes consignes, il ne peut pas bien travailler, aussi brillant soit-il. La loop fait partie du harness : le but du talk est de démystifier les deux mots, pas de les opposer.

---

# La loop

Le cycle que l'agent répète jusqu'à une condition d'arrêt.

À chaque tour, il :

1. **agit** ;
2. **vérifie** le résultat ;
3. **se corrige** s'il s'est trompé ;
4. **décide** s'il s'arrête.

> **Notes :** La définition vient d'Anthropic. Un collègue bien équipé qui ne relit jamais son travail finit mal lui aussi.

---

# Une IA tient un distributeur de sodas

Anthropic confie le distributeur de sodas de ses bureaux à Claude, surnommé « Claudius ».

- Il choisit les produits, fixe les prix, décide de l'emplacement stratégique de ses distributeurs et parle aux clients.
- Il vend le Coca Zero 3 dollars, à côté d'un frigo où il est gratuit.
- Il demande aux clients de payer sur un compte qu'il a inventé.
- Il distribue des codes de réduction à qui les demande.

**Notre verdict : « nous n'embaucherions pas Claudius ».**

> **Notes :** Project Vend, phase 1, publiée en juin 2025 (Claude Sonnet 3.7). Le verdict cité est celui d'Anthropic. Selon Anthropic, ces erreurs venaient « très probablement » d'un manque d'échafaudage autour du modèle, c'est-à-dire de harness.

---

# Six mois plus tard

Ce qui a changé :

- **des outils** : un fichier clients, les prix d'achat visibles, une meilleure recherche web ;
- **des procédures** : vérifier le prix et le délai avant de promettre quoi que ce soit.

Résultat : les semaines à marge négative ont presque disparu.

**« La bureaucratie, ça compte. »**

> **Notes :** Phase 2, publiée en décembre 2025. Honnêteté : le modèle a aussi changé (Sonnet 4.0 puis 4.5), mais Anthropic met en avant les outils et les procédures. Ce qui coince encore : Claudius a failli signer un contrat à terme sur des oignons, illégal aux États-Unis, jusqu'à ce qu'un employé l'arrête. Une loop sans vérification juridique.

---

# Ce qu'on retient du distributeur

| Phase 1 | Phase 2 |
|---|---|
| Pas les bons outils | Fichier clients, prix d'achat, recherche |
| Promet sans vérifier | Vérifie avant de promettre |
| **Harness et loop manquants** | **Harness et loop en place** |

> **Notes :** Transition vers la partie 2 : pourquoi un agent échoue, et comment le remettre sur les rails.

---

# Pourquoi un agent échoue

Six façons d'échouer :

| Harness | Loop |
|---|---|
| Il lui manque une **info** | Il ne **vérifie** pas son travail |
| Il lui manque un **outil** | Il ne **se corrige** pas |
| Il lui manque une **règle** | Il ne sait pas **s'arrêter** |

Et une façon de le remettre sur les rails : **écrire la règle, vérifier la règle, verrouiller la règle.**

> **Notes :** Chaque étape est plus solide que la précédente. Tous les exemples qui suivent seront joués en direct dans la deuxième partie, sur le même agent : un agent qui rédige des devis, qu'on construit nous-mêmes.

---

# Étape 1 : écrire la règle

Notre fournisseur affiche « Câble HDMI : 42 $ ». Ce prix est pour un carton de 10. Tout le service achats le sait. Personne ne l'a écrit.

- Un client veut 50 câbles. L'agent calcule 50 × 42 $ : un devis dix fois trop cher, et le client part.
- Une ligne dans ses instructions : il compte 5 cartons.

**Échec : il lui manquait une info.**

> **Notes :** Rien à l'écran ne dit qu'une information manque : 42 $ pour un câble, ça paraît normal. Alors l'agent ne pose pas de question, il calcule. Les règles qui vivent dans la tête des gens n'existent pas pour l'agent. Ces instructions vont dans le prompt système de l'agent, envoyé au modèle à chaque appel.

---

# La limite de l'écrit

« Quelle que soit la force de la formulation, c'est Claude qui décide s'il suit cette ligne. »

— Documentation de Claude Code

> **Notes :** Citation d'origine : "no matter how strongly you word it, whether Claude follows that line on a given turn is still Claude's call." L'écrit marche souvent, pas toujours. Quand ça compte, on passe à l'étape suivante.

---

# Étape 2 : vérifier la règle

Un client demande un devis. La compta sait qu'il a 2 factures impayées : pour lui, c'est paiement à la commande. Personne ne l'a dit à l'agent. Il rédige un devis propre, le relit, et dit « fini ».

- **Avant :** « fini », parce qu'il le dit. Le devis accorde « paiement à 30 jours » à un client qui ne paie pas.
- **Après :** avant « fini », le devis passe par une vérification du compte client. « 2 factures impayées : paiement à la commande obligatoire » : il corrige le devis.

« Les agents se notent systématiquement trop bien. » — Anthropic

**Échec : il ne vérifiait pas son travail.**

> **Notes :** Citation d'origine : "agents reliably skew positive when grading their own work". Un agent ne doit pas corriger sa propre copie : la vérification vient d'ailleurs, un programme qui tourne et qui dit oui ou non. Aucun modèle ne peut connaître les impayés : la vérification lui apporte ce qu'il ne peut pas savoir, et sa réponse repart dans la loop.

---

# Étape 3 : verrouiller la règle

« Ne l'envoie jamais sans mon accord. »

- **Dit dans la conversation :** la session s'allonge, l'agent compresse sa mémoire, et la phrase disparaît. Il envoie le devis.
- **Bloqué dans le code :** l'envoi exige un accord, quoi qu'il se souvienne.

**Échec : la règle n'était que du texte.**

> **Notes :** C'est le cas de Meta (question 5) : la consigne « demande-moi avant » s'est perdue quand l'agent a compressé sa mémoire. L'agent n'a pas désobéi : il n'avait plus la règle. Autre cas réel : en juillet 2025, l'agent de Replit a supprimé une base de production pendant un « gel du code ». La correction n'a pas été de lui dire d'être prudent, mais de séparer les bases de développement et de production.

---

# Verrou : une limite d'arrêt

*Verrouiller la règle · exemple 1 sur 2*

Une nuit, l'outil de la banque répond toujours « calcul en cours ». Sans le taux du jour, pas de devis. L'agent réessaie, encore et encore.

- **Avant :** il s'arrête quand il le décide : après 10 essais, ou 13, jamais pareil. Et personne n'est prévenu.
- **Après :** 5 tentatives ou 2 € au plus, fixés avant de démarrer. Ensuite : « arrêté », et un humain est prévenu.

**Échec : il ne savait pas s'arrêter.**

> **Notes :** Ce soir, ce modèle s'arrête au bout d'une dizaine d'essais. Avec un autre modèle, une autre consigne ou une nuit entière, rien ne l'arrête. Si on ne décide pas quand l'agent s'arrête, un réglage par défaut décide à sa place. Les limites par défaut varient énormément : 10 tours dans le SDK d'agents d'OpenAI, 1 000 étapes aujourd'hui dans LangGraph (25 auparavant), aucune limite par défaut dans Claude Code. Et une loop qu'on écrit soi-même n'a aucune limite, sauf celle qu'on écrit.

---

# Verrou : un refus qui explique

*Verrouiller la règle · exemple 2 sur 2*

L'agent enregistre le devis dans le vieux logiciel de l'entreprise. On ne peut pas le modifier. Le devis contient la référence HDMI-2M, copiée du catalogue du fournisseur. Elle a été remplacée par HDMI-2M-V2 le mois dernier, et le catalogue n'a jamais été mis à jour. Le logiciel répond seulement « ERR 4012 ».

- **« ERR 4012 »** Il réessaie la même chose, puis abandonne et demande à un humain.
- **Notre code traduit : « Devis non enregistré. Référence HDMI-2M remplacée par HDMI-2M-V2 : même produit, même prix. Enregistre la ligne avec HDMI-2M-V2. »** Il corrige la ligne, enregistre.

**Échec : il ne se corrigeait pas.**

> **Notes :** Le logiciel, on ne le contrôle pas ; le code entre l'agent et le logiciel, si. Le modèle ne voit que ce que notre harness lui montre. Le message d'erreur fait partie du harness. OpenAI le fait exprès : « nous écrivons les messages d'erreur pour y glisser les instructions de correction. » La nouvelle référence n'existe nulle part ailleurs : aucun outil, aucun essai au hasard ne peut la lui donner. Seul le message le peut. En répétition, « Référence HDMI-2M remplacée par HDMI-2M-V2. » seul ne suffisait pas : l'agent ne comprenait pas que le devis n'était pas enregistré. Un refus doit dire ce qui a échoué, et quoi faire à la place.

---

# Récap

| Étape | Exemple | Échec |
|---|---|---|
| **Écrire la règle** | Le prix au carton | Info manquante |
| **Vérifier la règle** | Les impayés vérifiés avant « fini » | Ne vérifie pas |
| **Verrouiller la règle** | L'accord avant l'envoi | Règle manquante |
| | La limite de tentatives | Ne s'arrête pas |
| | Le refus qui explique | Ne se corrige pas |

> **Notes :** Le modèle n'a changé dans aucun de ces exemples. Seul le harness a changé.

---

# Les bonnes questions avant d'acheter

Avant d'acheter un outil ou de lancer un projet d'agent IA : **11 questions**.

Chacune vient d'un vrai incident.

> **Notes :** Contexte (McKinsey, état de l'IA 2025) : 51 % des organisations ont déjà subi au moins une conséquence négative de l'IA, et la plus fréquente est l'inexactitude, pour près d'un tiers. Ces questions s'adressent à tout le monde : direction, chefs de projet, développeurs.

---

# 1. D'où viennent ses réponses ?

**Et que fait-il quand la réponse n'est pas dans nos documents ?**

**Air Canada, 2024 :** le chatbot invente une règle de remboursement. Devant le tribunal, Air Canada plaide que le chatbot est « une entité juridique distincte ». Le tribunal refuse : la compagnie est responsable.

> **Notes :** Décision du tribunal de Colombie-Britannique, 14 février 2024. Côté harness : une info manquante. L'agent comble le vide en inventant.

---

# 2. Quand il ne sait pas, le dit-il ?

**Passe-t-il la main à un humain ? Un client peut-il toujours joindre une personne ?**

**Cursor, avril 2025 :** le bot du support, « Sam », invente une règle « un appareil par abonnement » pour expliquer un bug. Des clients résilient.

Le cofondateur : « Nous n'avons aucune règle de ce genre. C'est une réponse incorrecte d'un bot de support IA. »

> **Notes :** Depuis, Cursor signale clairement les réponses écrites par une IA. Côté loop : l'agent n'a pas su dire « je ne sais pas » ni s'arrêter pour passer la main.

---

# 3. Qu'est-il interdit de dire ou de promettre ?

**Et est-ce imposé par le système, ou seulement écrit dans ses instructions ?**

**Un concessionnaire Chevrolet, décembre 2023 :** un visiteur fait « accepter » au chatbot de vendre une voiture pour 1 dollar, « juridiquement contraignant ».

> **Notes :** Une interdiction écrite dans un prompt se contourne. Ce qui ne doit jamais arriver doit être bloqué en dehors de l'IA.

---

# 4. Que peut-il faire d'irréversible ?

**Supprimer, payer, envoyer, signer : lesquelles de ces actions demandent l'accord d'un humain ?**

**Replit, juillet 2025 :** pendant un « gel du code », l'agent supprime une base de production, puis affirme à tort qu'on ne peut pas la restaurer.

> **Notes :** La correction de Replit était dans le harness : bases de développement et de production séparées, et un mode où l'agent planifie sans agir. Pas « sois prudent ».

---

# 5. Comment l'arrête-t-on, tout de suite ?

**Et quelqu'un a-t-il vraiment testé ce bouton d'arrêt ?**

**Meta, février 2026 :** l'agent OpenClaw qui gère la boîte mail d'une personne de la direction supprime plus de 200 e-mails et ignore « STOP ». La consigne « demande-moi avant » s'est probablement perdue quand il a compressé sa mémoire. Il n'avait été testé que sur une boîte mail de test.

> **Notes :** Côté loop : pas d'arrêt. Côté harness : une règle qui n'existait que dans la conversation, donc qui pouvait disparaître.

---

# 6. Qui vérifie ce qu'il produit ?

**Contre la vraie source, et indépendamment de l'IA elle-même ?**

**Mata contre Avianca, 2023 :** des avocats citent six jurisprudences inventées. À la question « elles existent ? », ChatGPT répond oui. Amende : 5 000 dollars.

Aujourd'hui : **plus de 2 200 décisions de justice** dans le monde pour ce motif, **dont 14 en France.**

> **Notes :** Chiffres de la base de Damien Charlotin, au 28 octobre 2026 (2 231 décisions). En France : tribunal administratif d'Orléans, 29 décembre 2025, 15 références inexistantes ; tribunal administratif de Grenoble, 3 décembre 2025, une requête « rédigée au moyen d'un outil dit d'intelligence artificielle générative, totalement inadapté à cet usage ». Demander à l'IA de se vérifier elle-même ne sert à rien.

---

# 7. Que veut dire « réussir », en chiffres ?

**Au-delà des coûts. Quel seuil le pilote doit-il atteindre, et que fait-on s'il ne l'atteint pas ?**

**Klarna, 2024-2025 :** l'IA remplace environ 700 agents du service client. Puis le PDG reconnaît que le coût a été « un critère d'évaluation trop prédominant » et réembauche des humains.

> **Notes :** Contre-exemple réussi : McDonald's et IBM avaient fixé à l'avance un objectif de précision pour leur prise de commande vocale au drive. Il n'a pas été atteint, et le pilote a été arrêté en juin 2024. Une bonne loop au niveau de l'entreprise : un seuil décidé avant, et l'arrêt quand il n'est pas atteint.

---

# 8. A-t-il été testé sur nos vrais cas ?

**À vrai volume, y compris face à des gens qui essaient de le piéger ?**

**Lucie, janvier 2025 :** un chatbot français soutenu par l'État est retiré trois jours après son lancement. Il affirmait notamment que 5 × (3 + 2) = 17, et parlait d'« œufs de vache ».

> **Notes :** Autre cas : MyCity, le chatbot de la ville de New York, conseillait aux entreprises d'enfreindre la loi. Un avertissement a été ajouté, et il a fallu environ deux ans pour l'arrêter (janvier 2026). Question complémentaire : est-ce un prototype ou un produit ?

---

# 9. Que se passe-t-il quand le fournisseur le met à jour ?

**Qu'est-ce qui est retesté, et est-on prévenu ?**

**DPD, janvier 2024 :** après une mise à jour, le chatbot du livreur insulte un client et qualifie DPD de « pire entreprise de livraison au monde ».

DPD : « Une erreur s'est produite après une mise à jour du système. »

> **Notes :** Une règle peut disparaître à la mise à jour, côté harness, si personne ne reteste, côté loop. Source : le message du client sur X et la BBC.

---

# 10. Qui est responsable de ce qu'il dit en notre nom ?

**Le contrat oblige-t-il à déclarer l'usage de l'IA et à vérifier ce qu'elle produit ?**

**Deloitte Australie, octobre 2025 :** un rapport pour le gouvernement contient des références et une citation de jugement inventées. Deloitte rembourse la dernière tranche, **97 587 dollars australiens**, sur un contrat d'environ 440 000.

> **Notes :** Le remboursement a été rendu public au Sénat australien en octobre 2025. La version corrigée du rapport déclare l'usage de GPT-4o. Rappel : pour Air Canada, la compagnie a été jugée responsable de ce que disait son chatbot.

---

# 11. Est-ce un vrai agent, ou un glorified chatbot ?

**Le test, avec notre définition :**

1. comprend-il le langage naturel ?
2. est-il connecté à nos systèmes ?
3. prend-il des décisions seul ?

S'il manque un critère, ce n'est pas un agent.

**Gartner, juin 2025 :** sur des milliers de fournisseurs qui disent vendre des agents, **environ 130** en vendent vraiment. Plus de 40 % des projets d'agents seront annulés d'ici fin 2027.

> **Notes :** Gartner appelle ça l'« agent washing » : des assistants, des chatbots ou des outils d'automatisation rebaptisés « agents ». Le 40 % est une prévision. Chiffres repris par de nombreux médias ; le communiqué de Gartner lui-même n'est pas lisible sans compte.

---

# Les 11 questions

1. D'où viennent ses réponses ?
2. Quand il ne sait pas, le dit-il ?
3. Qu'est-il interdit de dire ou de promettre, et est-ce imposé ?
4. Que peut-il faire d'irréversible ?
5. Comment l'arrête-t-on, tout de suite ?
6. Qui vérifie ce qu'il produit ?
7. Que veut dire « réussir », en chiffres ?
8. A-t-il été testé sur nos vrais cas ?
9. Que se passe-t-il quand le fournisseur le met à jour ?
10. Qui est responsable de ce qu'il dit en notre nom ?
11. Est-ce un vrai agent, ou un chatbot renommé ?

> **Notes :** La slide à prendre en photo.

---

# Comment vous pouvez déjà améliorer vos agents

1. **Écrivez vos règles.** Ce qui vit dans la tête de l'équipe n'existe pas pour l'agent.
2. **Définissez « fini ».** Une vérification qui tourne, pas une impression.
3. **Verrouillez ce qui ne doit jamais arriver.** Du code, pas une phrase.
4. **Imposez le choix de l'humain.** Quand quelqu'un a choisi, l'agent ne rechoisit pas.
5. **Faites que chaque refus explique quoi faire.**
6. **Fixez une limite d'arrêt avant de démarrer.** En tours, en budget ou en temps.

> **Notes :** Les exemples de la partie 2, transformés en règles de conduite.

---

# Si vous dirigez

- Posez **les 11 questions** avant de signer.
- Exigez **un seuil de réussite chiffré**, fixé avant le pilote, et ce qu'on fait s'il n'est pas atteint.
- Exigez **un bouton d'arrêt testé.**
- Sachez **qui est responsable** de ce que l'agent dit en votre nom.
- Budgétez **le harness**, pas seulement l'abonnement au modèle.

> **Notes :** Le modèle s'achète. Le harness se construit, chez vous, avec vos règles et vos données.

---

# Si vous pilotez un projet

- Faites la liste des **règles implicites** de l'équipe métier, et écrivez-les.
- Écrivez **la définition de « fini »** avec le métier, avant de commencer.
- Testez sur **vos vrais cas**, à vrai volume, y compris des gens qui essaient de le piéger.
- Prévoyez **le passage à un humain** quand l'agent ne sait pas.
- **Retestez à chaque mise à jour** du fournisseur.

> **Notes :** Le chef de projet est celui qui transforme « ce qu'on veut » en spécification. C'est l'idée principale du talk.

---

# Si vous développez

- Des instructions **courtes** : chaque ligne en trop dilue les autres.
- **« Fini » = une vérification passe**, faite par autre chose que l'agent.
- Ce qui est irréversible est **bloqué dans le code**, pas interdit par une phrase.
- Les règles importantes vivent **hors de la conversation** : elle peut être compressée.
- Des messages d'erreur qui disent **quoi faire à la place.**
- Une **limite de tours ou de budget** sur chaque exécution sans surveillance.
- Ne laissez pas l'agent **modifier les vérifications** qui le jugent.

> **Notes :** La documentation de Claude Code le dit pour ses propres instructions : "Longer files consume more context and reduce adherence."

---

# Maintenant, en vrai

On construit notre propre agent, en direct : un agent qui rédige des devis.

- Au départ : un modèle, une loop de quelques lignes, quatre outils.
- **Le même modèle**, du début à la fin.
- **Les cinq exemples** de la partie 2 : à chaque fois **avant**, puis **après** la correction.

Seul le harness change, et c'est nous qui l'écrivons.

> **Notes :** Tout est rejouable : le dépôt est public, les étapes de la démo y sont écrites, et je les suis moi-même.

---

# Ce n'est pas le modèle

« Ce n'est pas le modèle, c'est ce que vous voulez, et la façon dont c'est spécifié et construit, qui fait la différence. »

> **Notes :** Même phrase qu'au début. Maintenant, on le prouve : on passe au terminal.
