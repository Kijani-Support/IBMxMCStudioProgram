import { useI18n } from '../i18n/I18nContext';

export default function LanguageSwitcher() {
  const { lang, changeLang, languages } = useI18n();

  return (
    <select
      value={lang}
      onChange={(e) => changeLang(e.target.value)}
      className="text-sm border border-gray-300 rounded-lg px-2 py-1 bg-white text-gray-700 focus:ring-2 focus:ring-indigo-500"
    >
      {languages.map(l => (
        <option key={l.code} value={l.code}>{l.label}</option>
      ))}
    </select>
  );
}
