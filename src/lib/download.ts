export function downloadBytes(bytes: Uint8Array, fileName: string): void {
  const blob = new Blob([bytes as BlobPart], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  // Safari aborts the download if the URL is revoked synchronously after click().
  setTimeout(() => URL.revokeObjectURL(url), 100);
}
