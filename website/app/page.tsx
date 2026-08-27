"use client";

import { useState } from "react";

import { ErrorAlert } from "@/components/feedback/error-alert";
import { ModalHost } from "@/components/layout/modal-host";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { ComingSoonGrid } from "@/components/platform/coming-soon-grid";
import { UrlForm } from "@/components/url/url-form";
import { useDownloadSession } from "@/hooks/use-download-session";
import { useJobPolling } from "@/hooks/use-job-polling";
import { useProbe } from "@/hooks/use-probe";
import { ApiRequestError } from "@/lib/api/http-client";
import { isTerminal } from "@/lib/domain/job";
import { useModal } from "@/providers/modal-provider";

export default function Home() {
  const { open } = useModal();
  const { jobIds } = useDownloadSession();
  const { data: jobs = [] } = useJobPolling(jobIds);
  const [error, setError] = useState<string | null>(null);

  const probe = useProbe((result) => {
    setError(null);
    open(
      result.kind === "playlist"
        ? { name: "playlist", probe: result }
        : { name: "format", probe: result },
    );
  });

  const submit = (url: string) => {
    setError(null);
    probe.mutate(url, {
      onError: (cause) => {
        setError(
          cause instanceof ApiRequestError
            ? cause.message
            : "Could not read that link. Check it and try again.",
        );
      },
    });
  };

  const activeCount = jobs.filter((job) => !isTerminal(job.status)).length;

  return (
    <>
      <SiteHeader activeCount={activeCount} />

      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center gap-10 px-4 py-14 sm:py-20">
        <div className="space-y-6">
          <div className="space-y-3">
            <h1 className="font-display text-3xl leading-[1.1] font-700 tracking-tight sm:text-5xl">
              Paste a link.
              <br />
              <span className="text-muted-foreground">Get the file.</span>
            </h1>
            <p className="text-muted-foreground max-w-md text-sm">
              Video or audio, at the quality you pick. Whole playlists too.
            </p>
          </div>

          <UrlForm onSubmit={submit} isLoading={probe.isPending} />

          {error && <ErrorAlert message={error} />}
        </div>

        <ComingSoonGrid />
      </main>

      <SiteFooter />
      <ModalHost />
    </>
  );
}
