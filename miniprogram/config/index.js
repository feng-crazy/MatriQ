// 添加环境变量检查函数
function getEnv() {
  return process.env.NODE_ENV || 'development'
}

const config = {
  projectName: 'matriq-miniprogram',
  date: '2025-01-01',
  designWidth: 750,
  deviceRatio: {
    640: 2.34 / 2,
    750: 1,
    828: 1.81 / 2
  },
  sourceRoot: 'src',
  outputRoot: 'dist',
  plugins: [],
  defineConstants: {},
  framework: 'react',
  compiler: 'webpack5',
  cache: {
    type: 'memory'
  },
  // 根据环境变量设置是否启用 sourceMap
  terser: {
    enable: getEnv() === 'production' ? true : false,
    config: {
      // terser 配置选项
      compress: {
        drop_console: getEnv() === 'production' ? true : false
      }
    }
  },
  mini: {
    copy: {
      patterns: [
        { from: 'src/assets/', to: 'dist/src/assets/' }
      ]
    },
    postcss: {
      pxtransform: {
        enable: true,
        config: {}
      },
      url: {
        enable: true,
        config: {
          limit: 1024
        }
      },
      cssModules: {
        enable: false,
        config: {
          namingPattern: 'module',
          generateScopedName: '[name]__[local]___[hash:base64:5]'
        }
      }
    },
    // 添加别名配置
    alias: {
      '@': require('path').resolve(__dirname, '../src')
    }
  },
  h5: {
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
        config: {}
      },
      cssModules: {
        enable: false,
        config: {
          namingPattern: 'module',
          generateScopedName: '[name]__[local]___[hash:base64:5]'
        }
      }
    },
    // 添加别名配置
    alias: {
      '@': require('path').resolve(__dirname, '../src')
    }
  }
}

module.exports = function (merge) {
  if (process.env.NODE_ENV === 'development') {
    return merge({}, config, require('./dev'))
  }
  return merge({}, config, require('./prod'))
}