# Comment ajouter ta clé SSH sur GitHub

## Ta clé publique

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICopYUlRP+9FFXtNm+g1LuYgXa6s08cfCChdlwlDm4p/ yagami@yagami-X405UR
```

**Fingerprint** : `SHA256:17BSrY+x3xvt60fwH1KL7vnzwiuYm/TkE62kC9w1xlM`

---

## Étapes

1. **Copie la clé ci-dessus** (tout le contenu de `ssh-ed25519` jusqu'à la fin)

2. **Va sur GitHub** : https://github.com/settings/keys

3. **Clique sur "New SSH key"** (ou "Ajouter une clé SSH" en français)

4. **Remplis le formulaire** :
   - **Title** : `Yagami - Machine locale` (ou un nom de ton choix)
   - **Key** : Colle la clé complète que tu as copiée
   - **Key type** : `Authentication Key` (par défaut)

5. **Clique sur "Add SSH key"**

6. **Vérifie** : Tu devrais voir ta clé dans la liste avec le fingerprint `SHA256:17BSrY...`

---

## Test après ajout

Une fois ajoutée, teste la connexion :

```bash
ssh -T git@github.com
```

Tu devrais voir : `Hi krmultipro! You've successfully authenticated...`

Ensuite, tu pourras pousser ton commit :

```bash
git push origin dev
```

---

## Note de sécurité

✅ **C'est normal et sécurisé** d'utiliser la même clé SSH pour plusieurs services (VPS, GitHub, etc.).  
La clé publique peut être partagée, seule la clé privée doit rester secrète.

