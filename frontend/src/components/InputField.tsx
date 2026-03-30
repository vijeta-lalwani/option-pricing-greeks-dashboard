type InputFieldProps = {
  label: string;
  name: string;
  value: number;
  step?: string;
  onChange: (name: string, value: number) => void;
};

export function InputField({ label, name, value, step = "0.01", onChange }: InputFieldProps) {
  return (
    <label className="input-field">
      <span>{label}</span>
      <input
        type="number"
        name={name}
        value={value}
        step={step}
        onChange={(event) => onChange(name, Number(event.target.value))}
      />
    </label>
  );
}
