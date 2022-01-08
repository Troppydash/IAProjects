function integrate(fn, a, b, dx=0.01) {
  let x = a;
  let sum = 0;
  while (x <= b) {
    sum += fn(x) * dx;
    x += dx;
  }
  return sum;
}

function simulate() {
    const rolls = "LL"

    const xs = [];
    for (let i = 0; i <= 1; i+=0.01) {
        xs.push(i);
    }

    const priors = [];
    priors.push(x => 1);
    for (let i = 0; i < rolls.length; ++i) {
        const is_like = rolls[i] === "L";

        let likelihood;
        if (is_like) {
            likelihood = x => x;
        } else {
            likelihood = x => 1 - x;
        }

        const evidence = integrate(t => likelihood(t) * priors[i](t), 0, 1);
        console.log(evidence);
        priors[i+1] = x => likelihood(x) * priors[i](x) / evidence;

        const mean = integrate(t => t * priors[i+1](t), 0, 1);
        console.log(mean);
    }
}

simulate();
