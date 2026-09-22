export function PageTitle({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-5 flex flex-col justify-between gap-4 xl:flex-row xl:items-end">
      <div className="max-w-4xl">
        <div className="mosaic-label">{eyebrow}</div>
        <h1 className="mt-1.5 text-2xl font-extrabold tracking-tight text-[#17303d] sm:text-[28px]">
          {title}
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          {description}
        </p>
      </div>
      {action}
    </div>
  );
}
