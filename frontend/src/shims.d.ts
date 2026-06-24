// mammoth ships a self-contained browser bundle (with its own buffer polyfill) but no
// types for that entry, so we declare the small slice we use.
declare module 'mammoth/mammoth.browser' {
  interface ConvertResult {
    value: string
    messages: unknown[]
  }
  export function convertToHtml(input: { arrayBuffer: ArrayBuffer }): Promise<ConvertResult>
}
