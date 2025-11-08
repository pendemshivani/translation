module.exports = function override(config) {
  const oneOfRule = config.module.rules.find((rule) => Array.isArray(rule.oneOf));
  const svgRule = oneOfRule.oneOf.find((rule) => rule.test && rule.test.toString().includes("svg"));

  svgRule.use = [
    {
      loader: require.resolve("@svgr/webpack"),
      options: { icon: true },
    },
  ];

  return config;
};
