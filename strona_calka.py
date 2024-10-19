from flask import Flask, render_template, request, jsonify
import sympy as sp
import matplotlib.pyplot as plt
import io
import base64
from scipy.integrate import quad
import numpy as np


app = Flask(__name__)

# Funkcja do obliczania całki metodą prostokątów
def calka(wyrazenie, a, b, n):
    x = sp.Symbol('x')
    expr = sp.sympify(wyrazenie)
    
    podstawa_prostokata = (b - a) / n
    suma = 0
    for i in range(n):
        x_srodek = a + (i + 0.5) * podstawa_prostokata
        wysokosc_prostokata = float(expr.subs(x, x_srodek).evalf())  # Obliczamy wartość funkcji w środku prostokąta
        pole_prostokata = podstawa_prostokata * wysokosc_prostokata  # Pole prostokąta
        suma += pole_prostokata  # Dodajemy pole prostokąta do sumy
    
    return suma

# Endpoint do obsługi obliczeń z użyciem metody prostokątów
@app.route('/oblicz', methods=['POST'])
def oblicz():
    wyrazenie = request.form['funkcja']
    a = float(request.form['a'])
    b = float(request.form['b'])
    n = int(request.form['n'])  # Pobieramy liczbę prostokątów od użytkownika
    
    wynik = calka(wyrazenie, a, b, n)  # Obliczamy całkę metodą prostokątów z zadaną liczbą prostokątów
    
    # Upewnij się, że wynik jest floatem, zanim go zwrócisz
    return jsonify({'wynik': float(wynik)})


# Funkcja do rozwiązywania wyrażenia matematycznego za pomocą SymPy
def rozwiaz_wyrazenie(wyrazenie, x_srodek):
    x = sp.Symbol('x')
    expr = sp.sympify(wyrazenie)  # Bezpieczne przekształcenie wyrażenia
    return float(expr.subs(x, x_srodek).evalf())  # Upewniamy się, że wynik to liczba zmiennoprzecinkowa

# Główna strona
@app.route('/')
def index():
    return render_template('index.html')



# Endpoint do rysowania wykresu
@app.route('/rysuj', methods=['POST'])
def rysuj():
    # Odczytaj dane z formularza
    wyrazenie = request.form['funkcja']
    a = float(request.form['a'])
    b = float(request.form['b'])
    n = int(request.form['n'])

    # Tworzenie wykresu
    fig, ax = plt.subplots()

    # Definiujemy symboliczny x i wyrażenie jako funkcję NumPy
    x = sp.Symbol('x')
    expr = sp.sympify(wyrazenie)
    funkcja = sp.lambdify(x, expr, 'numpy')  # Tworzymy funkcję działającą na tablicach NumPy

    # Generujemy punkty x i odpowiadające im wartości y
    x_vals = np.linspace(a, b, n + 1)  # n+1 punktów, aby uwzględnić końce przedziału
    y_vals = funkcja(x_vals)

    # Generujemy punkty do rysowania wykresu funkcji
    x_wykres = np.linspace(a - 1, b + 1, 500)  # Szerszy zakres dla lepszego widoku
    y_wykres = funkcja(x_wykres)

    # Rysowanie wykresu funkcji
    ax.plot(x_wykres, y_wykres, label=f'f(x) = {wyrazenie}')

    # Rysowanie prostokątów metodą prostokątów
    ax.bar(x_vals[:-1], y_vals[:-1], width=(b - a) / n, align='edge', alpha=0.4, edgecolor='r')

    # Dodawanie opisu osi i siatki
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.legend()
    ax.grid(True)

    # Zapisz wykres do bufora
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Zwracanie obrazu w formacie base64
    encoded_img = base64.b64encode(buf.getvalue()).decode('utf-8')
    return jsonify({'wykres': encoded_img})





if __name__ == '__main__':
    app.run(debug=True)
