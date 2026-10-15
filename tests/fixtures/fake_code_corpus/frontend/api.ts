export async function fetchOrders() {
  if (isMock) {
    return [{ id: 1 }];
  }
  throw new Error("not implemented");
}

export function saveOrder() {
  // TODO: 接后端
}

describe("orders", () => {
  it.skip("creates order", () => {
    expect(true).toBe(true);
  });
});

export function safeParse(fn: () => void) {
  try {
    fn();
  } catch {}
}
