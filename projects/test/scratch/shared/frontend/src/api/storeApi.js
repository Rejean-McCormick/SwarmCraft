async function fetchProducts(){
  const res = await fetch('/api/products');
  return res.json();
}
export { fetchProducts };
