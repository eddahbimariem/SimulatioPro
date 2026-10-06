import matplotlib
try:
    matplotlib.use("TkAgg")      
except Exception:
    pass

import numpy as np
import matplotlib.pyplot as plt


# Données physiques de l'acétone


A, B, C = 4.42448, 1312.253, -32.445
TC = 508.1             
M = 58.08              
DHVAP_NB = 29.1        
T_NB = 329.2           
BAR_PAR_ATM = 1.01325


def t_ebullition(p_atm):
    """Température d'ébullition (K) à la pression p_atm (atm)."""
    p_bar = np.asarray(p_atm) * BAR_PAR_ATM
    return B / (A - np.log10(p_bar)) - C


def chaleur_latente(t_k):
    """Chaleur latente de vaporisation (kJ/kg) à T, relation de Watson."""
    dh_nb = DHVAP_NB * 1000 / M                      
    return dh_nb * ((1 - t_k / TC) / (1 - T_NB / TC)) ** 0.38


def saisir(texte, defaut, minimum=None, maximum=None):
    """Lit un nombre au clavier ; Entrée = valeur par défaut."""
    while True:
        rep = input(f"{texte} [{defaut}] : ").strip().replace(",", ".")
        try:
            val = float(rep) if rep else float(defaut)
        except ValueError:
            print("  -> Valeur invalide, entre un nombre.")
            continue
        if minimum is not None and val < minimum:
            print(f"  -> La valeur doit être >= {minimum}.")
            continue
        if maximum is not None and val > maximum:
            print(f"  -> La valeur doit être <= {maximum}.")
            continue
        return val


def main():

# Saisie des données 

    print("=== Séparation et vaporisation d'un flux d'acétone ===")
    print("(Appuie sur Entrée pour garder la valeur par défaut)\n")

    T_in = saisir("Température d'entrée (°C)", 10.0, minimum=-90, maximum=55)
    P_in = saisir("Pression (atm)", 1.0, minimum=0.01, maximum=40)
    debit = saisir("Débit massique total (kg/h)", 38.0, minimum=0.001)
    frac_1 = saisir("Fraction massique du flux 1 (%)", 40.0,
                    minimum=0, maximum=100)
    cp = saisir("Cp liquide de l'acétone (kJ/kg.K)", 2.17, minimum=0.1)
    p_min = saisir("Pression minimale de la courbe (atm)", 0.1, minimum=0.01)
    p_max = saisir("Pression maximale de la courbe (atm)", 3.0, minimum=0.02)
    n_pts = int(saisir("Nombre de points de la courbe", 25, minimum=2))

    if p_max <= p_min:
        print("Pression max <= pression min : valeurs par défaut utilisées.")
        p_min, p_max = 0.1, 3.0

    frac_2 = 100 - frac_1


#  Calculs
    
    m1 = debit * frac_1 / 100           
    m2 = debit * frac_2 / 100            

    T_eb_K = float(t_ebullition(P_in))
    T_eb_C = T_eb_K - 273.15

    if T_in >= T_eb_C:
        print("\nAttention : la température d'entrée est supérieure ou égale "
              "à la température d'ébullition, pas de chauffage sensible.")

    q_sensible = m2 * cp * max(T_eb_C - T_in, 0)     # kJ/h
    q_latent = m2 * chaleur_latente(T_eb_K)          # kJ/h
    q_total = q_sensible + q_latent                  # kJ/h
    q_kW = q_total / 3600

#Results

    print("\n================== RÉSULTATS ==================")
    print(f"Flux 1 ({frac_1:.0f} %) : {m1:.2f} kg/h")
    print(f"Flux 2 ({frac_2:.0f} %) : {m2:.2f} kg/h "
          f"(chauffé jusqu'à vaporisation)")
    print(f"\n1) Température d'ébullition à {P_in} atm :")
    print(f"   {T_eb_K:.2f} K = {T_eb_C:.2f} °C")
    print("\n2) Énergie pour transformer le flux 2 en vapeur :")
    print(f"   Chauffage du liquide : {q_sensible:10.1f} kJ/h")
    print(f"   Vaporisation         : {q_latent:10.1f} kJ/h")
    print(f"   Énergie totale       : {q_total:10.1f} kJ/h = {q_kW:.3f} kW")
    print("===============================================")

    
    #  Courbe T_ébullition = f(P)
    
    P_atm = np.linspace(p_min, p_max, n_pts)
    T_K = t_ebullition(P_atm)

    print("\n3) Tableau de la courbe :")
    print(f"{'N°':>3} {'P (atm)':>10} {'P (Pa)':>12} {'T (K)':>10}")
    for i, (p, t) in enumerate(zip(P_atm, T_K), start=1):
        print(f"{i:>3} {p:>10.3f} {p * 101325:>12.1f} {t:>10.3f}")

    plt.figure(figsize=(9, 5))
    plt.plot(P_atm, T_K, marker="o", color="#1F6080", linewidth=2,
             label="Courbe d'ébullition")
    plt.plot(P_in, T_eb_K, "r*", markersize=15,
             label=f"Point étudié ({P_in} atm ; {T_eb_K:.1f} K)")
    plt.title("Variation de la température d'ébullition de l'acétone\n"
              "en fonction de la pression")
    plt.xlabel("Pression (atm)")
    plt.ylabel("Température d'ébullition (K)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig("courbe_ebullition_acetone.png", dpi=150)
    print("\nGraphique enregistré : courbe_ebullition_acetone.png")
    print("Ferme la fenêtre du graphique pour terminer le programme.")
    plt.show()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")