/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import react from '@vitejs/plugin-react';
import {resolve} from 'path';
import {defineConfig} from 'vite';
import styleX from 'vite-plugin-stylex';
import viteTsconfigPaths from 'vite-tsconfig-paths';

// Normalize `c:\foo\index.html` to `c:/foo/index.html`.
// This affects Rollup's `facadeModuleId` (which expects the `c:/foo/bar` format),
// and is important for Vite to replace the script tags in HTML files.
// See https://github.com/vitejs/vite/blob/7440191715b07a50992fcf8c90d07600dffc375e/packages/vite/src/node/plugins/html.ts#L804
// Without this, building on Windows might produce HTML entry points with
// missing `<script>` tags, resulting in a blank page.
function normalizeInputPath(inputPath: string) {
  return process.platform === 'win32' ? resolve(inputPath).replace(/\\/g, '/') : inputPath;
}

// TODO: this could be a glob on src/platform/*.html
const platforms = {
  main: normalizeInputPath('index.html'),
  androidStudio: normalizeInputPath('androidStudio.html'),
  androidStudioRemote: normalizeInputPath('androidStudioRemote.html'),
  webview: normalizeInputPath('webview.html'),
  chromelikeApp: normalizeInputPath('chromelikeApp.html'),
};

export default defineConfig({
  base: '',
  plugins: [
    react({
      babel: {
        plugins: [
          ['@babel/plugin-proposal-decorators', {legacy: true}],
          [
            'jotai/babel/plugin-debug-label',
            {
              customAtomNames: [
                'atomFamilyWeak',
                'atomLoadableWithRefresh',
                'atomWithOnChange',
                'atomWithRefresh',
                'configBackedAtom',
                'jotaiAtom',
                'lazyAtom',
                'localStorageBackedAtom',
              ],
            },
          ],
          'jotai/babel/plugin-react-refresh',
        ],
      },
    }),
    styleX(),
    viteTsconfigPaths(),
  ],
  build: {
    outDir: 'build',
    manifest: true,
    rollupOptions: {
      input: platforms,
    },
  },
  server: {
    // No need to open the browser, it's opened by `yarn serve` in `isl-server`.
    open: false,
    port: 3000,
  },
});
