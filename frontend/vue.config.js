module.exports = {
  devServer: {
    proxy: {
      "^/api": {
        target: "http://localhost:5000",
      },
    },
  },
  pwa: {
    icons: null,
  },
};
