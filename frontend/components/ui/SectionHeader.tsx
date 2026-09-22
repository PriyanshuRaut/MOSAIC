export function SectionHeader({
  title,
  description,
  right,
}: {
  title: string;
  description?: string;
  right?: React.ReactNode;
}) {
  return (
    <div className="mosaic-card-header flex items-start justify-between gap-4 px-5 py-4">
      <div>
        <h2 className="text-sm font-bold text-slate-800">{title}</h2>
        {description ? (
          <p className="mt-1 text-xs leading-5 text-slate-500">{description}</p>
        ) : null}
      </div>
      {right}
    </div>
  );
}
