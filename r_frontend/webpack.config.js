const path = require('path');

module.exports = {
  entry: './src/index.js', // Punto de entrada de tu código
  output: {
    // Aquí defines la carpeta de salida para el bundle.
    // Ajusta la ruta según donde tengas tus archivos estáticos en Django.
    path: path.resolve(__dirname, '../static/js'),
    filename: 'bundle.js'
  },
  mode: 'development', // Cambia a 'production' en producción
  module: {
    rules: [
      // Aquí puedes agregar reglas para procesar otros tipos de archivos (por ejemplo, Babel para ES6)
    ]
  }
};
